#!/usr/bin/env python3
import os
import argparse

def save_file(file_path, code_lines, doc_root, debug=False):
    """
    指定された相対パス (file_path) を基に、doc_root以下にファイルを保存します。
    必要なディレクトリが存在しない場合は自動生成します。
    """
    target_path = os.path.join(doc_root, file_path)
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, 'w', encoding='utf-8') as f:
        f.writelines(code_lines)
    print(f"Created: {target_path}")
    if debug:
        print(f"[DEBUG] Saved {len(code_lines)} lines to {target_path}")

def main():
    parser = argparse.ArgumentParser(
        description="Markdownファイルから各ファイルを復元するスクリプトです。\n"
                    "入力Markdownは、各ファイルパスが単独行に記載され、その後にコードブロックが続く形式を想定します。"
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
    parser.add_argument(
        '--debug',
        action='store_true',
        help="デバッグ出力を有効にする"
    )
    args = parser.parse_args()
    debug = args.debug

    if not os.path.exists(args.input):
        print(f"入力ファイル {args.input} が見つかりません。")
        return

    doc_root = os.path.abspath(args.doc_root)
    if debug:
        print(f"[DEBUG] Using document root: {doc_root}")
        print(f"[DEBUG] Reading input file: {args.input}")

    with open(args.input, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_file = None    # 現在のファイルパス（文字列）
    code_lines = []        # 現在のコードブロックの内容（リスト）
    inside_code_block = False  # コードブロック内かどうか

    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if debug:
            print(f"[DEBUG] Line {line_number}: {stripped}")

        # 区切り行（==== など）はスキップ
        if stripped.startswith("===="):
            if debug:
                print(f"[DEBUG] Skipping separator line at {line_number}")
            continue

        # コードブロックの開始／終了判定
        if stripped.startswith("```"):
            if not inside_code_block:
                # コードブロック開始
                inside_code_block = True
                if debug:
                    print(f"[DEBUG] Entering code block at line {line_number}")
                continue
            else:
                # コードブロック終了
                inside_code_block = False
                if current_file:
                    if debug:
                        print(f"[DEBUG] Exiting code block at line {line_number} for file '{current_file}'")
                    save_file(current_file, code_lines, doc_root, debug)
                else:
                    if debug:
                        print(f"[DEBUG] Exiting code block at line {line_number} but no current file set")
                # リセット
                current_file = None
                code_lines = []
                continue

        # コードブロック内の行はそのまま蓄積
        if inside_code_block:
            code_lines.append(line)
            if debug:
                print(f"[DEBUG] Appended line {line_number} to current code block (current file: {current_file})")
        else:
            # コードブロック外：空行でなく、かつバッククォート行でない場合、ファイルパス行とみなす
            if stripped != "":
                # ファイルパスとみなす（単に1行に書かれていると仮定）
                current_file = stripped
                if debug:
                    print(f"[DEBUG] Detected file header at line {line_number}: '{current_file}'")
            else:
                if debug:
                    print(f"[DEBUG] Skipping empty line at {line_number}")

    # もし最後までコードブロックが閉じられなかった場合の処理
    if inside_code_block and current_file and code_lines:
        if debug:
            print(f"[DEBUG] End of file reached. Saving last file '{current_file}'")
        save_file(current_file, code_lines, doc_root, debug)

if __name__ == "__main__":
    main()
