#!/usr/bin/env python3
import os
import argparse

def is_binary_file(file_path, blocksize=512):
    """
    ファイルの先頭部分をチェックして、バイナリファイルかどうか判定します。
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(blocksize)
            if b'\0' in chunk:
                return True
            return False
    except Exception:
        # エラー時は安全のためバイナリ扱いにする
        return True

def main():
    parser = argparse.ArgumentParser(
        description="指定したドキュメントルート内のテキストファイルを再帰的に探索し、1枚のMarkdownにまとめます。"
    )
    parser.add_argument(
        '-o', '--output',
        default='output.md',
        help="出力するMarkdownファイルのパス（例: ../all_code.md）"
    )
    parser.add_argument(
        '--doc-root',
        default=os.getcwd(),
        help="ソースコード探索のドキュメントルート（例: ../my_project）"
    )
    parser.add_argument(
        '--exclude',
        nargs='*',
        default=[],
        help="探索から除外するディレクトリ名のリスト（例: .git venv）"
    )
    args = parser.parse_args()

    # 指定されたドキュメントルートを絶対パスに変換
    doc_root = os.path.abspath(args.doc_root)

    with open(args.output, 'w', encoding='utf-8') as out_md:
        for root, dirs, files in os.walk(doc_root):
            # 除外ディレクトリや隠しディレクトリはスキップ
            dirs[:] = [d for d in dirs if d not in args.exclude and not d.startswith('.')]
            for file in files:
                file_path = os.path.join(root, file)
                # ドキュメントルートからの相対パスを求める
                rel_path = os.path.relpath(file_path, doc_root)
                # 自身のスクリプトがドキュメントルート内にある場合は除外
                if os.path.abspath(file_path) == os.path.abspath(__file__):
                    continue
                if is_binary_file(file_path):
                    continue
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    # UTF-8で読み込めなければlatin1で試す
                    try:
                        with open(file_path, 'r', encoding='latin1') as f:
                            content = f.read()
                    except Exception:
                        continue
                except Exception:
                    continue

                # ファイルパスを見出しとして出力
                out_md.write(f"## {rel_path}\n\n")

                # 拡張子からシンタックスハイライト用の言語指定（未知の場合は"text"）
                ext = os.path.splitext(file)[1].lower()
                mapping = {
                    '.py': 'python',
                    '.js': 'javascript',
                    '.java': 'java',
                    '.c': 'c',
                    '.cpp': 'cpp',
                    '.h': 'cpp',
                    '.html': 'html',
                    '.css': 'css',
                    '.json': 'json',
                    '.xml': 'xml',
                    '.md': 'markdown',
                    '.sh': 'bash',
                    '.rb': 'ruby',
                    '.go': 'go'
                }
                lang = mapping.get(ext, "text")

                # コードブロックとして内容を出力
                out_md.write(f"```{lang}\n")
                out_md.write(content)
                if not content.endswith("\n"):
                    out_md.write("\n")
                out_md.write("```\n\n")

if __name__ == "__main__":
    main()
