import base64
import binascii
import json
import os
from datetime import datetime
from typing import Optional


MTIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def current_mtime() -> str:
    return datetime.now().strftime(MTIME_FORMAT)


class VfsNode:
    def __init__(
        self,
        name: str,
        is_dir: bool,
        content: str = "",
        meta: Optional[dict] = None,
    ) -> None:
        self.name = name
        self.is_dir = is_dir
        self.content = content
        metadata = meta or {}
        default_perm = "rwxr-xr-x" if is_dir else "rw-r--r--"
        self.permissions = metadata.get("permissions") or default_perm
        self.owner = metadata.get("owner", "root")
        self.mtime = metadata.get("mtime", "2026-09-28 10:00:00")
        self.size = self._calc_size(metadata.get("size"), is_dir, content)
        self.children: dict[str, "VfsNode"] = {}

    @staticmethod
    def _calc_size(
        given_size: Optional[int],
        is_dir: bool,
        content: str,
    ) -> int:
        if given_size is not None:
            return given_size
        if not is_dir and content:
            try:
                return len(base64.b64decode(content.encode("ascii")))
            except (ValueError, binascii.Error):
                return len(content)
        return 4096 if is_dir else 0


def _parse_vfs_dict(name: str, data: dict) -> VfsNode:
    if not isinstance(data, dict):
        raise ValueError("Элемент VFS должен быть объектом")

    node_type = data.get("type")
    if node_type not in ("dir", "file"):
        raise ValueError(f"Неизвестный тип узла VFS: {node_type}")

    meta = {
        "permissions": data.get("permissions"),
        "owner": data.get("owner", "root"),
        "mtime": data.get("mtime", "2026-09-28 10:00:00"),
        "size": data.get("size"),
    }
    if node_type == "file":
        return VfsNode(
            name=name,
            is_dir=False,
            content=data.get("content", ""),
            meta=meta,
        )

    node = VfsNode(name=name, is_dir=True, meta=meta)
    raw_children = data.get("children", {})
    if not isinstance(raw_children, dict):
        raise ValueError("Поле children для папки должно быть объектом")

    for child_name, child_data in raw_children.items():
        node.children[child_name] = _parse_vfs_dict(child_name, child_data)
    return node


class Vfs:
    def __init__(self) -> None:
        self.root = VfsNode(name="/", is_dir=True)

    def load_from_json(self, filepath: str) -> None:
        if not filepath:
            return

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Файл VFS не найден: {filepath}")

        try:
            with open(filepath, "r", encoding="utf-8") as file_handle:
                data = json.load(file_handle)
        except json.JSONDecodeError as decode_err:
            raise ValueError(
                f"Неверный формат JSON в VFS: {decode_err}"
            ) from decode_err

        if not isinstance(data, dict) or data.get("type") != "dir":
            raise ValueError("Корневой элемент VFS должен быть директорией")

        self.root = _parse_vfs_dict("/", data)

    def dump_structure(self) -> list[str]:
        result: list[str] = []

        def _traverse(node: VfsNode, path: str) -> None:
            kind = "dir" if node.is_dir else "file"
            meta_str = (
                f"[{kind}, {node.permissions}, {node.owner}, {node.size}B]"
            )
            result.append(f"{path} {meta_str}")
            if node.is_dir:
                for child_name in sorted(node.children.keys()):
                    child = node.children[child_name]
                    child_path = f"{path.rstrip('/')}/{child_name}"
                    _traverse(child, child_path)

        _traverse(self.root, "/")
        return result

    @staticmethod
    def split_path(path_str: str) -> list[str]:
        return [part for part in path_str.split("/") if part]

    def resolve_path(self, cwd: str, target: str) -> str:
        parts = [] if target.startswith("/") else self.split_path(cwd)
        for segment in target.split("/"):
            if not segment or segment == ".":
                continue
            if segment == "..":
                if parts:
                    parts.pop()
            else:
                parts.append(segment)
        return "/" + "/".join(parts)

    def get_node(self, canonical_path: str) -> Optional[VfsNode]:
        if canonical_path == "/":
            return self.root

        current = self.root
        segments = self.split_path(canonical_path)
        for part in segments:
            if not current.is_dir or part not in current.children:
                return None
            current = current.children[part]
        return current

    def list_dir(self, canonical_path: str) -> list[str]:
        node = self.get_node(canonical_path)
        if node is None:
            raise FileNotFoundError(f"Каталог не найден: {canonical_path}")
        if not node.is_dir:
            raise NotADirectoryError(f"Не является каталогом: {canonical_path}")
        return sorted(node.children.keys())

    def read_file(self, canonical_path: str) -> str:
        node = self.get_node(canonical_path)
        if node is None:
            raise FileNotFoundError(f"Файл не найден: {canonical_path}")
        if node.is_dir:
            raise IsADirectoryError(f"Является каталогом: {canonical_path}")

        try:
            raw_bytes = base64.b64decode(node.content.encode("ascii"))
            return raw_bytes.decode("utf-8", errors="replace")
        except (ValueError, binascii.Error) as err:
            return f"[Ошибка декодирования base64: {err}]"

    def touch(self, canonical_path: str) -> None:
        node = self.get_node(canonical_path)
        if node is not None:
            node.mtime = current_mtime()
            return

        segments = self.split_path(canonical_path)
        if not segments:
            raise ValueError("Нельзя создать файл с пустым именем")

        file_name = segments[-1]
        parent_path = "/" + "/".join(segments[:-1])
        parent_node = self.get_node(parent_path)
        if parent_node is None:
            raise FileNotFoundError(
                f"Родительский каталог не найден: {parent_path}"
            )
        if not parent_node.is_dir:
            raise NotADirectoryError(
                f"Родительский путь не каталог: {parent_path}"
            )

        parent_node.children[file_name] = VfsNode(
            name=file_name,
            is_dir=False,
            meta={"mtime": current_mtime()},
        )

    def _validate_move_source(
        self,
        src_path: str,
    ) -> tuple[VfsNode, VfsNode, str]:
        if src_path == "/":
            raise PermissionError("Нельзя перемещать корневой каталог")

        src_node = self.get_node(src_path)
        if src_node is None:
            raise FileNotFoundError(f"Источник не найден: {src_path}")

        src_segments = self.split_path(src_path)
        src_name = src_segments[-1]
        src_parent = self.get_node("/" + "/".join(src_segments[:-1]))
        if src_parent is None:
            raise FileNotFoundError("Родитель источника не найден")

        return src_node, src_parent, src_name

    def _move_to_new_name(
        self,
        src_parent: VfsNode,
        src_node: VfsNode,
        src_name: str,
        dst_path: str,
    ) -> None:
        dst_segments = self.split_path(dst_path)
        new_name = dst_segments[-1]
        dst_parent = self.get_node("/" + "/".join(dst_segments[:-1]))
        if dst_parent is None or not dst_parent.is_dir:
            raise FileNotFoundError("Целевой каталог назначения не существует")

        del src_parent.children[src_name]
        src_node.name = new_name
        dst_parent.children[new_name] = src_node

    def move(self, src_path: str, dst_path: str) -> None:
        if dst_path == src_path:
            return

        src_node, src_parent, src_name = self._validate_move_source(src_path)
        if src_node.is_dir and (dst_path + "/").startswith(src_path + "/"):
            raise ValueError("Нельзя переместить каталог в свой подкаталог")

        dst_node = self.get_node(dst_path)
        if dst_node is not None and dst_node.is_dir:
            del src_parent.children[src_name]
            dst_node.children[src_name] = src_node
            return

        if dst_node is not None and src_node.is_dir:
            raise ValueError("Нельзя заменить файл каталогом")

        self._move_to_new_name(src_parent, src_node, src_name, dst_path)
