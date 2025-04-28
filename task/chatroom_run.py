import asyncio
import os
import sys
os.environ['DATABASE_AUTO_COMMIT'] = 'True'

from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent))

from core.chatroom import ChatroomManager

        
if __name__ == '__main__':

    if os.environ.get('CONDA_PREFIX'):
        os.environ['TESSDATA_PREFIX'] = os.environ['CONDA_PREFIX'] + '/share/tessdata'
        
    import nltk
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')

    
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    manager = ChatroomManager(event_loop)
    event_loop.create_task(manager.start())
    try:
        event_loop.run_forever()
    except KeyboardInterrupt:
        manager.stop()
    all_tasks = asyncio.all_tasks(event_loop)
    event_loop.run_until_complete(asyncio.gather(*all_tasks, return_exceptions=True))
    event_loop.stop()
    event_loop.close()
