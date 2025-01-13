
from datetime import datetime
import pytz
curr_time = lambda: datetime.now().isoformat()

class log:
    @classmethod
    def init(cls, name):
        cls.__name = name

    @classmethod
    def logi(cls, log):
        # text = curr_time
        text = f'[..]: {log}\n'
        with open(cls.__name, 'a') as f:
            f.write(text)
        print(text)

    @classmethod
    def loge(cls, log):
        # text = f'{curr_time} [!!]: {log}\n'
        text = f'[!!]: {log}\n'
        with open(cls.__name, 'a') as f:
            f.write(text)
        print(text)