# -*- coding: utf-8 -*-
"""
ĐỀ TÀI 7: MÔ PHỎNG CẤU TRÚC HỆ THỐNG TẬP TIN
CTDL sử dụng: Cây đa phân (N-ary Tree)

PHÂN CÔNG NHÓM 3 NGƯỜI:
  - Thành viên 1: PHẦN 1 - Lớp Node + các lệnh mkdir, touch, pwd
  - Thành viên 2: PHẦN 2 - Tìm đường dẫn + các lệnh ls, cd
  - Thành viên 3: PHẦN 3 - Lệnh find (DFS) + Giao diện dòng lệnh (shell) + Phân tích độ phức tạp

Cách chạy:  python file_system.py
"""


# ======================================================================
# PHẦN 1 (THÀNH VIÊN 1): NODE + mkdir + touch + pwd
# ======================================================================

class FileSystemError(Exception):
    """Lỗi riêng của hệ thống tập tin (tên trùng, không tìm thấy, ...)."""
    pass


class Node:
    """
    Một nút trong cây đa phân. Có thể là THƯ MỤC hoặc TẬP TIN.
      - Thư mục: có thể chứa nhiều nút con  -> children là dict {tên: Node}
      - Tập tin: là nút lá, không có con    -> children = None
    Dùng dict để tra cứu nút con theo tên nhanh (trung bình O(1)).
    """

    def __init__(self, name, is_dir, parent=None):
        self.name = name          # tên thư mục/tập tin
        self.is_dir = is_dir      # True = thư mục, False = tập tin
        self.parent = parent      # nút cha (để thực hiện cd .. và pwd)
        self.children = {} if is_dir else None


class FileSystem:
    """Quản lý toàn bộ cây thư mục và thư mục hiện tại."""

    def __init__(self):
        self.root = Node("", True)     # thư mục gốc "/"
        self.current = self.root       # thư mục đang đứng

    # ---------- Hàm phụ: kiểm tra tên hợp lệ ----------
    def _check_name(self, name):
        if name == "" or name in (".", ".."):
            raise FileSystemError(f"Tên không hợp lệ: '{name}'")
        if "/" in name:
            raise FileSystemError("Tên không được chứa dấu '/'")

    # ---------- Hàm phụ: thêm một nút con vào thư mục hiện tại ----------
    def _add(self, name, is_dir):
        self._check_name(name)
        if name in self.current.children:
            raise FileSystemError(f"'{name}' đã tồn tại")
        self.current.children[name] = Node(name, is_dir, self.current)

    # ---------- mkdir: tạo thư mục mới ----------
    def mkdir(self, name):
        self._add(name, True)

    # ---------- touch: tạo tập tin mới ----------
    def touch(self, name):
        self._add(name, False)

    # ---------- pwd: đường dẫn của một nút (mặc định là thư mục hiện tại) ----------
    def pwd(self, node=None):
        node = node or self.current
        parts = []
        while node.parent is not None:     # đi ngược từ nút lên gốc
            parts.append(node.name)
            node = node.parent
        parts.reverse()                    # đảo lại thành gốc -> nút
        return "/" + "/".join(parts)


    # ==================================================================
    # PHẦN 2 (THÀNH VIÊN 2): TÌM ĐƯỜNG DẪN + ls + cd
    # ==================================================================

    def _resolve(self, path):
        """
        Chuyển chuỗi đường dẫn thành nút tương ứng.
        Hỗ trợ: tuyệt đối (/a/b), tương đối (a/b), '.' và '..'
        """
        if path == "":
            raise FileSystemError("Thiếu đường dẫn")

        # Bắt đầu từ gốc nếu đường dẫn bắt đầu bằng '/', ngược lại từ thư mục hiện tại
        node = self.root if path.startswith("/") else self.current

        for part in path.split("/"):
            if part == "" or part == ".":
                continue                       # bỏ qua phần rỗng và '.'
            if part == "..":
                if node.parent is not None:    # gốc thì giữ nguyên
                    node = node.parent
                continue
            # Đi xuống nút con; nút hiện tại phải là thư mục và có con tên 'part'
            if not node.is_dir or part not in node.children:
                raise FileSystemError(f"Không tìm thấy: {path}")
            node = node.children[part]
        return node

    # ---------- ls: liệt kê nội dung thư mục hiện tại ----------
    def ls(self):
        # Thư mục thêm dấu '/' phía sau để dễ phân biệt với tập tin
        return [(n.name + "/") if n.is_dir else n.name
                for n in self.current.children.values()]

    # ---------- cd: đổi thư mục ----------
    def cd(self, path):
        target = self._resolve(path)
        if not target.is_dir:
            raise FileSystemError(f"'{path}' không phải là thư mục")
        self.current = target


    # ==================================================================
    # PHẦN 3 (THÀNH VIÊN 3): find (DFS) + SHELL + ĐỘ PHỨC TẠP
    # ==================================================================

    def find(self, name):
        """
        Tìm tất cả tập tin/thư mục có tên = name trong TOÀN BỘ cây
        bằng DFS (duyệt theo chiều sâu). Trả về danh sách đường dẫn.
        """
        result = []
        self._dfs(self.root, name, result)
        return result

    def _dfs(self, node, name, result):
        # B1: xét nút hiện tại (bỏ qua gốc vì gốc không có tên)
        if node.parent is not None and node.name == name:
            result.append(self.pwd(node))
        # B2: nếu là thư mục thì đệ quy xuống từng con (đi sâu trước)
        if node.is_dir:
            for child in node.children.values():
                self._dfs(child, name, result)


# ----------------------------------------------------------------------
# GIAO DIỆN DÒNG LỆNH (SHELL)
# ----------------------------------------------------------------------
HELP = """Các lệnh:
  mkdir <tên>   tạo thư mục        touch <tên>  tạo tập tin
  ls            liệt kê            cd <đường dẫn>  đổi thư mục (hỗ trợ .. và /)
  pwd           đường dẫn hiện tại  find <tên>   tìm trong toàn bộ cây (DFS)
  help          xem trợ giúp       exit         thoát"""


def main():
    fs = FileSystem()
    print("=== MÔ PHỎNG HỆ THỐNG TẬP TIN ===")
    print(HELP)

    while True:
        # Dấu nhắc lệnh hiển thị đường dẫn hiện tại
        line = input(f"\n{fs.pwd()} $ ").strip()
        if line == "":
            continue
        parts = line.split(maxsplit=1)          # tách lệnh và đối số
        cmd = parts[0]
        arg = parts[1].strip() if len(parts) > 1 else ""

        try:
            if cmd == "mkdir":
                fs.mkdir(arg)
            elif cmd == "touch":
                fs.touch(arg)
            elif cmd == "ls":
                items = fs.ls()
                print("  ".join(items) if items else "(trống)")
            elif cmd == "cd":
                fs.cd(arg if arg else "/")       # cd không đối số -> về gốc
            elif cmd == "pwd":
                print(fs.pwd())
            elif cmd == "find":
                if arg == "":
                    raise FileSystemError("Thiếu tên cần tìm")
                found = fs.find(arg)
                if found:
                    print("\n".join(found))
                else:
                    print(f"Không tìm thấy '{arg}'")
            elif cmd == "help":
                print(HELP)
            elif cmd == "exit":
                print("Tạm biệt!")
                break
            else:
                print("Lệnh không tồn tại. Gõ 'help' để xem trợ giúp.")
        except FileSystemError as e:
            print("Lỗi:", e)


# ----------------------------------------------------------------------
# PHÂN TÍCH ĐỘ PHỨC TẠP (n = tổng số nút, k = số con của 1 thư mục,
#                         d = độ sâu của cây)
#
#   mkdir / touch : O(1)       (dict: kiểm tra trùng + thêm đều O(1) trung bình)
#   ls            : O(k)       (duyệt k con của thư mục hiện tại)
#   cd            : O(d)       (đi từng thành phần của đường dẫn, mỗi bước O(1))
#   pwd           : O(d)       (đi ngược từ nút lên gốc)
#   find (DFS)    : O(n * d)   (thăm n nút; mỗi nút khớp tên tốn O(d) để dựng đường dẫn)
#                   ~ O(n) nếu chỉ tính việc duyệt cây
#   Bộ nhớ DFS    : O(d)       (độ sâu ngăn xếp đệ quy)
# ----------------------------------------------------------------------

if __name__ == "__main__":
    main()
