# ScriptForChatGPT
ChatGPTを便利に使うための魔法のスクリプト集

## collect_sources.py
1. **これはなに**  
ドキュメントルート以下のファイルを全部まとめてMarkdownにするスクリプト  
それぞれのファイルはコードブロックにまとまっていて、コードブロックの前にはルートディレクトリからの相対パスが表示されるよ。  
ChatGPTにそのままお願いしたい時にコピペするだけでいいから便利だね。  

2. **使い方**
```bash
# 例：ドキュメントルートが ../path/to/my_project で、出力Markdownを ../all_code.md に出力する場合。
# 出力除外ファイルが .git venv の場合。
chmod +x collect_sources.py
./collect_sources.py --doc-root ../path/to/my_project -o ../all_code.md --exclude .git venv
```

## restore_sources.py
1. **これはなに**  
ChatGPTに出力してもらったMarkdownをいい感じにルートディレクトリ以下のフォルダに配置するスクリプト  
ChatGPTから出力してくれた巨大なシステムコードをちびちびコピペする手間を省けて便利

2. **使い方**  

2.1. ChatGPTに魔法の呪文を唱える。  
いい感じに調整して使ってください。

```text
本システムの最新の全ソースコードを、一切省略せず全部分出力してください。
ソースコードはコードブロックで書いてください。ソースコード以外の部分は地の文で書いてください。
それぞれのソースコードのコードブロックの一行前には、ドキュメントルートからのファイルパスを書いてください。ドキュメントルートからのファイルパス以外の文字は書かないでください。
```

2.2. スクリプト実行

```bash
# 例：入力Markdownが ../all_code.md で、復元先ドキュメントルートが ../path/to/my_project の場合
chmod +x restore_sources.py
./restore_sources.py -i ../all_code.md --doc-root ../path/to/my_project
```
