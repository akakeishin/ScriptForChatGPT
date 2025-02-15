#!/usr/bin/env python3
import os
import re
import argparse


def extract_file_path(line: str) -> str | None:
    """
    行からファイルパスを抽出します。以下の形式に対応：
      - "File: backend/docker-compose.yaml"
      - "## backend/docker-compose.yaml"
      - "1. **backend/docker-compose.yaml**" などのMarkdown装飾付き
      - 単独行で "data_quality_manager.py" など（拡張子が含まれる場合）
    """
    s = line.strip()
    if not s:
        return None

    # 複数のパターンで抽出を試みる
    patterns = [
        r"^File:\s*(.+)$",  # File: backend/docker-compose.yaml
        r"^#+\s*(.+)$",  # # backend/docker-compose.yaml  または ## 〜
        r"^\d+\.\s*\*\*(.+?)\*\*$",  # 1. **backend/docker-compose.yaml**
        r"^-+\s*\*\*(.+?)\*\*$",  # - **backend/docker-compose.yaml**
        r"^-?\s*\*\*(.+?)\*\*$",  # **backend/docker-compose.yaml** (前に - があっても)
        r"^\*\*(.+?)\*\*$",  # **backend/docker-compose.yaml**
    ]
    for pat in patterns:
        m = re.match(pat, s)
        if m:
            candidate = m.group(1).strip()
            return candidate

    # 拡張子が含まれる単独行とみなす（よく使う拡張子のリスト）
    known_exts = (
        ".py",
        ".txt",
        ".md",
        ".yaml",
        ".yml",
        ".json",
        ".dockerfile",
        ".sh",
        ".html",
        ".css",
    )
    if s.endswith(known_exts):
        return s

    # "/" が含まれていればファイルパスとみなす
    if "/" in s:
        return s

    return None


def save_file(
    file_path: str, code_lines: list[str], doc_root: str, debug: bool = False
) -> None:
    """
    指定された file_path（ドキュメントルートからの相対パス）に対して、
    code_lines の内容を保存します。必要なディレクトリがなければ作成します。
    """
    normalized_path = os.path.normpath(file_path)
    target_path = os.path.join(doc_root, normalized_path)
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "w", encoding="utf-8") as f:
        f.writelines(code_lines)
    print(f"Created: {target_path}")
    if debug:
        print(f"[DEBUG] Saved {len(code_lines)} lines to {target_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Markdownファイルから各ファイルを復元するスクリプトです。\n"
        "入力Markdownは、各ファイルパスが単独行またはMarkdownヘッダーとして記載され、その後にコードブロックが続く形式を想定します。"
    )
    parser.add_argument(
        "-i",
        "--input",
        default="all_code.md",
        help="入力Markdownファイルのパス（例: ../all_code.md）",
    )
    parser.add_argument(
        "--doc-root",
        default=os.getcwd(),
        help="復元先のドキュメントルート（例: ../my_project）",
    )
    parser.add_argument("--debug", action="store_true", help="デバッグ出力を有効にする")
    args = parser.parse_args()
    debug = args.debug

    if not os.path.exists(args.input):
        print(f"入力ファイル {args.input} が見つかりません。")
        return

    doc_root = os.path.abspath(args.doc_root)
    if debug:
        print(f"[DEBUG] Using document root: {doc_root}")
        print(f"[DEBUG] Reading input file: {args.input}")

    with open(args.input, "r", encoding="utf-8") as f:
        lines = f.readlines()

    current_file: str | None = None
    code_lines: list[str] = []
    inside_code_block = False

    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if debug:
            print(f"[DEBUG] Line {line_number}: {stripped}")

        # 区切り行（==== など）はスキップ
        if stripped.startswith("===="):
            if debug:
                print(f"[DEBUG] Skipping separator line at {line_number}")
            continue

        # コードブロックの開始／終了の判定
        if stripped.startswith("```"):
            if not inside_code_block:
                inside_code_block = True
                if debug:
                    print(f"[DEBUG] Entering code block at line {line_number}")
                continue
            else:
                inside_code_block = False
                if current_file:
                    if debug:
                        print(
                            f"[DEBUG] Exiting code block at line {line_number} for file '{current_file}'"
                        )
                    save_file(current_file, code_lines, doc_root, debug)
                else:
                    if debug:
                        print(
                            f"[DEBUG] Exiting code block at line {line_number} but no current file set"
                        )
                current_file = None
                code_lines = []
                continue

        # コードブロック内の行はそのまま蓄積
        if inside_code_block:
            code_lines.append(line)
            if debug:
                print(
                    f"[DEBUG] Appended line {line_number} to current code block (current file: {current_file})"
                )
        else:
            # コードブロック外で空行はスキップ
            if stripped == "":
                if debug:
                    print(f"[DEBUG] Skipping empty line at {line_number}")
                continue
            # ファイルパス行として抽出
            candidate = extract_file_path(line)
            if candidate:
                current_file = candidate
                if debug:
                    print(
                        f"[DEBUG] Detected file header at line {line_number}: '{current_file}'"
                    )
            else:
                if debug:
                    print(f"[DEBUG] No file header detected at line {line_number}")

    # 最後までコードブロックが閉じられていない場合の処理
    if inside_code_block and current_file and code_lines:
        if debug:
            print(f"[DEBUG] End of file reached. Saving last file '{current_file}'")
        save_file(current_file, code_lines, doc_root, debug)


if __name__ == "__main__":
    main()
