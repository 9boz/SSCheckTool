# SSCheckTool
<img width="742" height="696" alt="image" src="https://github.com/user-attachments/assets/5669b366-1c2e-403f-8aed-26d4b3238fd1" />

データのチェック時間短縮と精度を上げるためのツールです。  

## インストール　と　起動

- インストール
  SSCheckTool フォルダをpythonPathが通っている場所に格納してください。

  例）C:/Users/9boz/Documents/maya/2025/scripts

- 起動方法

Mayaを起動し、以下のコマンドをpython で実行してください。  

```python
import SSCheckTool
SSCheckTool.editable()
```

<img width="749" height="711" alt="image" src="https://github.com/user-attachments/assets/a916002e-149b-4a51-a2ab-4ceb920fa7df" />


## GUI 説明

<img width="305" height="124" alt="image" src="https://github.com/user-attachments/assets/b0a156d1-8b79-4334-8809-b0fafc2e2f19" />

- **topNode**
一部のチェックモジュールにて、特定の階層下のノードのみを対象とする場合に指定します。

- **check all**  
全てのチェック項目を実行します。

- **refresh result**  
チェック結果を消去します。

- **export result**  
チェック結果をファイルに保存します。


<img width="323" height="277" alt="image" src="https://github.com/user-attachments/assets/bc051d94-437a-4d0b-9577-df275a8f9ced" />

チェック項目が  
**項目名　　個別チェック実行ボタン　結果表示ボタン　修正処理ボタン**  
を1セットとして並びます。  

- **結果表示ボタン**
項目のチェック結果を色で知らせます。  
  
水色 = 引っかかったものがない  
黄色 = 致命設定はされていないが、なにか引っかかった  
赤色 = 致命設定がされており、なにか引っかかった  

ボタンを押下することで、右側のエリアに結果が表示されます。  

- **修正処理ボタン**  
チェックモジュールに修正処理が実装されている場合には使用可能状態になり、
それぞれの修正処理を実行します。

<img width="426" height="697" alt="image" src="https://github.com/user-attachments/assets/ac0094f3-6d8d-4915-870d-d4c6f1cbc1d9" />

- **モジュール概要**  
上部に現在結果を表示しているチェック項目の概要が表示されます。  

- **チェック結果**  
下部のリストにチェックで引っかかった項目がリストされます。
選択可能なものであれば、リスト上で選択することでシーン内の該当物を選択できます。  

<img width="234" height="114" alt="image" src="https://github.com/user-attachments/assets/ff6a3abc-f517-4475-9cd6-f617c83683ca" />

- **preset**
登録されているチェック項目のプリセットが表示され、選択するとプリセットを切り替えます。  


<img width="265" height="96" alt="image" src="https://github.com/user-attachments/assets/820a3e3e-ce33-4217-b138-3bdeb4710d06" />

- **setting > result export path**  
チェック結果を保存する先を指定します。  
  
- **setting > reset setting**  
プリセットを all 状態にし、各種設定をリセットします。

<img width="326" height="116" alt="image" src="https://github.com/user-attachments/assets/2cd321e5-df9c-4dee-9e8b-766224554c5d" />

- **edit > edit preset**  
プリセットを編集するためのダイアログを呼び出します。

<img width="405" height="535" alt="image" src="https://github.com/user-attachments/assets/7ed9f0f2-ff6d-4398-aa77-a94fab02589a" />

各項目を選択すると、下部にチェックモジュールの概要が表示されます。  
プリセットに入れたい場合は useをチェック状態（黒）にします。  
対象項目を致命的として扱う場合には fatalをチェック状態(黒)にします。  

- **save**
  現在選択しているプリセットを更新します。

- **save as**
  新しいプリセットを作成します。
  プリセット名は半角英数以外動作確認していません。  


## チェックモジュール説明

チェックモジュールは SSCheckTool/src/checkCommands 以下に格納されています。  

comment と def check(topNode,**kwargs)　は必須です。  
def correct(correctTargets,**kwargs) は任意です。

```python
import maya.cmds as cmds
from ..SPLib import editTransform

#チェック項目の概要説明(必須)
comment = "list animationLayers in this scene"
        
##--------------------------------------------------------------------------------                

#修正挙動（不要な場合にはコメントアウト）
def correct(correctTargets,**kwargs):            
    cmds.delete(correctTargets)

#チェック挙動（必須）
def check(topNode,**kwargs):
    result = []

    ignors = ["defaultLayer"]
    allNodes = editTransform.listTypeNodes("animLayer",topNode = None,fullpath =True)
    result = list(set(allNodes) - set(ignors))
        
    return result
```

## 免責

これらの手法・コードを使用したことによって引き起こる直接的、間接的な損害に対し、当方は一切責任を負うものではありません。
