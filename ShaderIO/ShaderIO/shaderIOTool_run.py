# coding:utf-8

import sys

def shaderIOTool_run():
    try:
        filePath = __file__
        appPath = filePath.rpartition('\\')[0]
    except:
        print 'Environ Value {} not exist.'.format(appPath)
    
    else:
        path = appPath
        
        if not path in sys.path:
            sys.path.append(path)
        
        import shaderUI
        reload(shaderUI)
        shaderUI.main()
        
if __name__ == 'shaderIOTool_run':  
    shaderIOTool_run()



