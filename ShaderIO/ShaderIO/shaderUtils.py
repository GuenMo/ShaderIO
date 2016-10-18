# coding:utf-8

import pymel.all as pm
import json

def getShadingEngine():
    """씬안에 Shadeing Engine을 검색해 리턴 한다.
    
    :returns: [nt.ShadingEngine]
    :rtype: list
    
    """
    
    sgGrps = pm.ls(type='shadingEngine')
    validSgGrp = []
    for sg in sgGrps:
        if sg.name() != 'initialParticleSE' and sg.name() != 'initialShadingGroup':
            validSgGrp.append(sg)
            
    return validSgGrp        

def getShaderInfo(shadingEngine):
    """ 입력 받은 shading Engine으로 부터 surface shader, displacement, geometry 값을 얻어 
    json으로 넘기기 위해  dict 으로 리턴 한다.
    
    :param shadingEngine: shading Engine
    :type shadingEngine: nt.ShadingEngine
    :returns: {'surfaceShader': surfaceShader, 'displacement':displacementShader, 'geometry':geometries}
    :rtype: dict
    
    .. note:: geometry는 shape 이름들의 list 입니다.

    """
    surface      = shadingEngine.surfaceShader.inputs()
    displacement = shadingEngine.displacementShader.inputs()
    geometry     = pm.listConnections(shadingEngine, type='mesh')
    
    if surface:
        surfaceShaderName = surface[0].name()
    else:
        surfaceShaderName = ''
    
    if displacement:
        displacementShaderName = displacement[0].name()
    else:
        displacementShaderName = ''
    
    geometryList = []
    for geo in geometry:
        geometryList.append(geo.name())
    
    info = {'surfaceShader': surfaceShaderName, 'displacement':displacementShaderName, 'geometry':geometryList}
    
    return info

def exportShader(path):
    """씬안에 쉐이딩 그룹으로 부터 정보를 모아 shaderInfoNode에 저장 한후 
    입력 받은 경로에 shader를 저장 한다.
    
    :param path: 파일 경로
    :type path: str
    
    """
    sgGrps = getShadingEngine()
    
    shaderInfos = []
    exportList = []
    
    for sg in sgGrps:
        shaderInfo = getShaderInfo(sg)
        shaderInfos.append(shaderInfo)
        if shaderInfo['surfaceShader'] != '':
            exportList.append(shaderInfo['surfaceShader'])
        if shaderInfo['displacement'] != '':
            exportList.append(shaderInfo['displacement'])
        
    numAttr = len(shaderInfos)
    
    if pm.objExists('shaderInfoNode'):
        shaderInfoNode = pm.PyNode('shaderInfoNode')
        shaderInfoNode.unlock()
        pm.delete(shaderInfoNode)
    shaderInfoNode = pm.createNode('network', n='shaderInfoNode')
    shaderInfoNode.addAttr('shaderInfos',  at = 'compound' , nc = numAttr)
    
    for i in range(numAttr):
        attrName = 'shaderInfos' + str(i)
        shaderInfoNode.addAttr(attrName, dt='string', p = 'shaderInfos')
    
    for i, shaderInfo in enumerate(shaderInfos):
        attrName = 'shaderInfos' + str(i)
        jsonHandl = json.dumps(shaderInfo)
        shaderInfoNode.attr(attrName).set(jsonHandl)
        shaderInfoNode.attr(attrName).lock()
    
    shaderInfoNode.lock()
    
    exportList.append(shaderInfoNode)
    pm.select(exportList)
    try:
        pm.exportSelected(path, pr=1, typ='mayaBinary', force=1, es=1)
        print 'Success Export Shader'
    except:
        print exportList
        print path
    
    finally:
        shaderInfoNode.unlock()
        pm.delete(shaderInfoNode)
            
def importShader(path):
    """입력 받은 경로에 shader를 import 한후 쉐이더를 적용 한다.
    
    :param path: 파일 경로
    :type path: str
    
    """
    try:
        pm.importFile(path)
        print 'Success import {}'.format(path)
    except:
        print 'Failed import {}'.format(path)
        return
    assignShader()

def assignShader():
    """씬안에서 shaderInfoNode 노드를 검색 한다.\n
    shaderInfoNode 노드에 shaderInfos# 어트리뷰트를 검색한다.\n
    shaderInfos# 어트리뷰트의 값을 json 으로 가져 온다.\n
    어트리뷰트의 geometry, surfaceShader, displacement 키 값을 가져 온다.\n
    geometry에 surfaceShader, displacement 적용 한다.\n
    shaderInfoNode 삭제 한다.
    
    .. warning:: 
        씬안에 'shaderInfoNode' 노드가 없을 때 ``shaderInfoNode not exist!`` 예외 발생
    """
    try:
        shaderInfoNode = pm.PyNode('shaderInfoNode')
    except:
        print '"shaderInfoNode" not exist!'
    
    numAttr = shaderInfoNode.shaderInfos.numChildren()
    
    message = ''
    for i in range(numAttr):
        shaderInfos = json.loads(shaderInfoNode.attr('shaderInfos{}'.format(i)).get())
        geos=[]
        for geo in shaderInfos.get('geometry'):
            if pm.objExists(geo):
                geos.append(geo)
        try:
            pm.select(geos)
            
            surfaceShader = pm.PyNode(shaderInfos.get('surfaceShader'))
            pm.hyperShade(assign=surfaceShader)
            pm.select(cl=True)    
            try:
                if shaderInfos.get('displacement'):
                    displacement = pm.PyNode(shaderInfos.get('displacement'))
                    sg = surfaceShader.outColor.outputs()[0]
                    displacement.displacement.connect(sg.displacementShader)
            except:
                message += ( str(shaderInfos.get('displacement')) + '-->' + sg.name()+ '\n')
        except:
            message += ( str(shaderInfos.get('surfaceShader')) + '-->' + str(geos )+ '\n')
            

    shaderInfoNode.unlock()
    pm.delete(shaderInfoNode)
    
    if message:
        print 'Failed list:\n'
        print message
        
def getYetiInfo():
    '''씬안에 pgYetiMaya 검색해 적용된 쉐이더와 트렌스폼이 딕셔너리로 리턴 한다.
    
    :returns: {transform: shader ..}
    :rtype: dict 
    
    .. note:: 
        transform: pgYetiMaya 노드의 transform 이름\n
        shader: pgYetiMaya 노드가 적용된 shader 이름
    '''
    nodes = pm.ls(type='pgYetiMaya')
    yetiInfo = {}
    
    for node in nodes:
        sg = node.instObjGroups.outputs()[0]
        surfaceShader = sg.surfaceShader.inputs()[0]
        yetiInfo[node.getParent().name()] = surfaceShader.name()
    return yetiInfo

def exportYeti(path):
    yeitInfo = getYetiInfo()
    if pm.objExists('yetiInfoNode'):
        yetiInfoNode = pm.PyNode('yetiInfoNode')
        yetiInfoNode.unlock()
        pm.delete(yetiInfoNode)
    
    attrName = 'yetiInfo'
    yetiInfoNode = pm.createNode('network', n='yetiInfoNode')
    yetiInfoNode.addAttr(attrName,  dt='string')
    jsonHandl = json.dumps(yeitInfo)
    yetiInfoNode.attr(attrName).set(jsonHandl)
    yetiInfoNode.attr(attrName).lock()
    yetiInfoNode.lock()
    
    exportList = [yetiInfoNode]
    for _, shader in yeitInfo.items():
        exportList.append(shader)

    pm.select(exportList)
    try:
        pm.exportSelected(path, pr=1, typ='mayaBinary', force=1, es=1)
        print 'Success Export Shader'
    except:
        print exportList
        print path
    finally:
        yetiInfoNode.unlock()
        pm.delete(yetiInfoNode)

def importYeti(path):
    """입력 받은 경로에 shader를 import 한후 쉐이더를 적용 한다.
    
    :param path: 파일 경로
    :type path: str
    
    """
    yetiInfo = getYetiInfo()
    if yetiInfo:
        for yetiNode, shader in yetiInfo.items():
            if pm.objExists(yetiNode):
                pm.delete(yetiNode)
            if pm.objExists(shader):
                pm.delete(shader)
    
    if pm.objExists('yetiInfoNode'):
        yetiInfoNode = pm.PyNode('yetiInfoNode')
        yetiInfoNode.unlock()
        pm.delete(yetiInfoNode)
    
    
    pm.importFile(path)
    if not pm.objExists('yetiInfoNode'):
        pm.error(u'"yetiInfoNode"가 존재 하지 않습니다.')
    
    yetiInfoNode = pm.PyNode('yetiInfoNode')
    yetiInfo = json.loads(yetiInfoNode.yetiInfo.get())
    
    for yetiNodeName, shaderName in yetiInfo.items():
        yetiNode = pm.createNode('pgYetiMaya', n=yetiNodeName + 'Shape')
        yetiParent = yetiNode.getParent()
        yetiParent.rename(yetiNodeName)
        yetiNode.renderDensity.set(1)
        yetiNode.aiOpaque.set(0)
        
        pm.select(yetiParent)
        surfaceShader = pm.PyNode(shaderName)
        pm.hyperShade(assign=surfaceShader)
      

    
    