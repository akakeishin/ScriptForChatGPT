#!/usr/bin/env python3
import os
import re
import argparse

def extract_file_path(line):
    """
    ファイルパスを含む行から、ドキュメントルートからの相対パスを抽出します。
    複数のフォーマットに対応：
      - **File: backend/requirements.txt**
      - File: backend/main.py
      - # File: backend/xxx など
    """
    patterns = [
        r"\*\*File:\s*(.+?)\*\*",  # **File: backend/xxx**
        r"^\s*File:\s*(\S+)",       # 行頭に File: backend/xxx
        r"^#+\s*File:\s*(\S+)"      # 見出し形式（例: "# File: backend/xxx"）
    ]
    for pat in patterns:
        m = re.search(pat, line)
        if m:
            return m.group(1).strip()
    return None

def save_file(rel_path, code_lines, doc_root):
    """
    指定された相対パス (rel_path) を基に、doc_root以下にファイルを保存します。
    必要なディレクトリが存在しない場合は自動生成します。
    """
    target_path = os.path.join(doc_root, rel_path)
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, 'w', encoding='utf-8') as f:
        f.writelines(code_lines)
    print(f"Created: {target_path}")

def main():
    parser = argparse.ArgumentParser(
        description="Markdown出力から各ファイルを復元するスクリプトです。"
    )
    parser.add_argument(
        '-i', '--input',
        default='all_code.md',
        help="入力Markdownファイルのパス（例: ../all_code.md）"
    )
    parser.add_argument(
        '--doc-root',
        default=os.getcwd(),
        help="復元先のドキュメントルート（例: ../my_project）"
    )
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"入力ファイル {args.input} が見つかりません。")
        return

    # 指定された復元先ドキュメントルートを絶対パスに変換
    doc_root = os.path.abspath(args.doc_root)

    with open(args.input, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_file = None   # 現在処理中のファイルの相対パス
    code_lines = []       # 現在のコードブロックの内容
    in_code_block = False # コードブロック内かどうかのフラグ

    for line in lines:
        # 区切り行（---）は無視
        if line.strip() == '---':
            continue

        # ファイルパスが記載された行を検出（複数のフォーマットに対応）
        candidate = extract_file_path(line)
        if candidate:
            # 前のファイルがあれば、書き出してからリセット
            if current_file is not None and code_lines:
                save_file(current_file, code_lines, doc_root)
                code_lines = []
            current_file = candidate
            continue

        # コードブロックの開始／終了を判定
        if line.lstrip().startswith("```"):
            if not in_code_block:
                # コードブロック開始（開始行はスキップ）
                in_code_block = True
            else:
                # コードブロック終了
                in_code_block = False
                if current_file is not None:
                    save_file(current_file, code_lines, doc_root)
                current_file = None
                code_lines = []
            continue

        # コードブロック内の行はファイル内容として蓄積
        if in_code_block:
            code_lines.append(line)

    # もしファイルが閉じられずに残っていた場合
    if current_file is not None and code_lines:
        save_file(current_file, code_lines, doc_root)

if __name__ == "__main__":
    main()
