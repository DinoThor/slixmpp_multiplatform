import ast
import os
import sys
import tomlkit

OLD_MODULE = "slixmpp"
NEW_MODULE = "slixmpp_multiplatform"

class SlixmppImportTransformer(ast.NodeTransformer):
    def visit_Import(self, node):
        """
          import slixmpp => import slixmpp_multiplatform as slixmpp
        """
        for alias in node.names:
            if alias.name == OLD_MODULE:
                alias.name = NEW_MODULE
                alias.asname = OLD_MODULE 
        return node

    def visit_ImportFrom(self, node):
        """
          from slixmpp import bar => from slixmpp_multiplatform import bar
          from slixmpp.foo import bar => from slixmpp_multiplatform.foo import bar
        """
        if node.module == OLD_MODULE:
            node.module = NEW_MODULE
        elif node.module and node.module.startswith(OLD_MODULE + "."):
            node.module = node.module.replace(OLD_MODULE, NEW_MODULE, 1)
        return node


def transform_code(code: str) -> str:
    tree = ast.parse(code)
    transformer = SlixmppImportTransformer()
    transformer.visit(tree)
    ast.fix_missing_locations(tree)

    return ast.unparse(tree)


def process_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        original = f.read()

    transformed = transform_code(original)

    if transformed != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(transformed)
        print(f"Modified: {filepath}")


def walk_and_process():
    for root, _, files in os.walk("slixmpp/slixmpp_multiplatform"):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                process_file(path)


def rename_toml():
    with open("slixmpp/pyproject.toml", "r+", encoding="utf-8") as f:
        data = tomlkit.parse(f.read())
        data["project"]["name"] = "slixmpp_multiplatform"
        f.seek(0)
        f.write(tomlkit.dumps(data))
        f.truncate()

def rename_cargo_toml():
    with open("slixmpp/Cargo.toml", "r+", encoding="utf-8") as f:
        data = tomlkit.parse(f.read())
        data["package"]["name"] = "slixmpp_multiplatform"
        data["lib"]["path"] = "slixmpp_multiplatform/jid.rs"
        f.seek(0)
        f.write(tomlkit.dumps(data))
        f.truncate()


def rename_sourcedir():
    os.rename('slixmpp/slixmpp', 'slixmpp/slixmpp_multiplatform')


if __name__ == "__main__":
    rename_sourcedir()
    rename_toml()
    rename_cargo_toml()
    walk_and_process()
