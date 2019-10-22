import json
import shutil
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
import ansible.constants as C
import redis
import datetime
import logging,logging.handlers

ansible_remote_user = 'root'

class ResultCallback(CallbackBase):
    """一个简单的回调插件 """
    def v2_runner_on_ok(self, result, **kwargs):
        """打印结果的json表示形式 """
        host = result._host
        print(json.dumps({host.name: result._result}, indent=4))

#调用需要传入 3 个参数，分别是 执行主机列表、任务列表、inventory 文件，
def AnsibleApi(hosts,tasks,soruces):
    # 构建一个解析器，将相关参数传入
    Options = namedtuple('Options', [
        'remote_user',
        'connection',
        'module_path',
        'forks',
        'become',
        'become_method',
        'become_user',
        'check',
        'diff'])
    options = Options(remote_user=ansible_remote_user,
                      connection='paramiko',
                      module_path=['/to/mymodules'],
                      forks=10,
                      become=None,
                      become_method=None,
                      become_user=None,
                      check=False,
                      diff=False)
    
    # 初始化所需对象
    loader = DataLoader() # 负责查找和读取yAML、json和ini文件
    passwords = dict(vault_pass='secret')
    
    # 实例化 ResultCallback，处理返回的结果。
    results_callback = ResultCallback()
    
    # 创建 inventory，定义需要执行的主机组
    inventory = InventoryManager(loader=loader, sources=sources)
    
    # 合并所有不同来源的参数
    variable_manager = VariableManager(loader=loader, inventory=inventory)
    
    # 创建数据结构来加载任务
    play_source =  dict(
            name = "Ansible Play",
            hosts = hosts,
            gather_facts = 'no',
            tasks = tasks)
    
    # 创建play对象，使用 .load 初始化
    play = Play().load(play_source, variable_manager=variable_manager, loader=loader)
    
    # 实例化任务队列管理器，它负责设置所有对象，以便在主机列表和任务上迭代
    tqm = None
    try:
        tqm = TaskQueueManager(
                  inventory=inventory,
                  variable_manager=variable_manager,
                  loader=loader,
                  options=options,
                  passwords=passwords,
                  stdout_callback=results_callback,  # 使用自定义回调函数
              )
        result = tqm.run(play) # 执行任务
    finally:
        # 清理子进程等相关数据
        if tqm is not None:
            tqm.cleanup()
        # 删除临时目录
        shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)


if __name__ == '__main__':
    tasks = []
    tasks.append(dict(action=dict(module='shell', args='ls'), register='shell_out'))
    tasks.append(dict(action=dict(module='debug', args=dict(msg='{{shell_out.stdout}}'))))
    sources = 'scripts/inventory'
    AnsibleApi("localhost",tasks,sources)
