from pathlib import Path

def parse_users(path: Path) -> dict[str, str]:
    users = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        parts = line.strip().split(":", 1)
        if len(parts) != 2:
            continue
        u, c = parts
        users[u] = c
    return users

def parse_products(path: Path) -> list[dict]:
    items = []
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split(":")
        if len(parts) != 3:
            continue
        nombre, cantidad, precio = parts
        items.append({"nombre": nombre, "cantidad": cantidad, "precio": precio})
    return items

def test_usuarios_txt_formato_y_credenciales(tmp_path: Path):
    (tmp_path / "usuarios.txt").write_text(
        "admin:1234\nusuario1:pass1\n\nmalformada\n111:111\n",
        encoding="utf-8",
    )
    users = parse_users(tmp_path / "usuarios.txt")
    assert users["admin"] == "1234"
    assert users["usuario1"] == "pass1"
    assert users["111"] == "111"
    assert "malformada" not in users  # línea inválida ignorada

def test_productos_txt_parsea_y_ignora_corruptas(tmp_path: Path):
    (tmp_path / "productos.txt").write_text(
        "camisa:2:19.99\n"
        "corrupta\n"
        "pantalon:1:29.50\n"
        "mal:1\n",
        encoding="utf-8",
    )
    productos = parse_products(tmp_path / "productos.txt")
    assert productos == [
        {"nombre": "camisa", "cantidad": "2", "precio": "19.99"},
        {"nombre": "pantalon", "cantidad": "1", "precio": "29.50"},
    ]
