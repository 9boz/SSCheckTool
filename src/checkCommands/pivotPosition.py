import maya.cmds as cmds
from ..SPLib import editTransform
comment =  "List transformNodes with pivot != [0.0,0.0,0.0]"

        
##--------------------------------------------------------------------------------                
        
def correct(correctTargets,**kwargs):

    for target in correctTargets:
        try:
            cmds.makeIdentity(target, a =True,t =True, r=True, s =True)
            cmds.xform(target,zeroTransformPivots =True)
        except:
            pass

    return


def check(topNode,**kwargs):
    ignors = []
    result = []
    if topNode != None:
        topNode = editTransform.getFullPathName(topNode)
        
    allNodes = editTransform.listTypeNodes("transform",ignorNodeTypes=["joint","camera","light","constraint"],topNode = topNode,fullpath =True)
    allNodes = list(set(allNodes)- set(ignors))

    for node in allNodes:
        pivotPosition = cmds.xform(node,q=True,ws =True,piv=True)[:3]

        for value in pivotPosition:
            if round(value,5) != 0.0:
                if node not in result:
                    result.append(node)
                    break

    return result


