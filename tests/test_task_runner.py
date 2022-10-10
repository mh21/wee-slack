import slack
from slack import Future, create_task, weechat_task_cb


def test_run_single_task():
    slack.active_tasks = {}
    slack.active_responses = {}
    future = Future[str]()

    async def awaitable():
        result = await future
        return "awaitable", result

    task = create_task(awaitable())
    weechat_task_cb(future.id, "data")

    assert not slack.active_tasks
    assert slack.active_responses == {task.id: ("awaitable", ("data",))}


def test_run_nested_task():
    slack.active_tasks = {}
    slack.active_responses = {}
    future = Future[str]()

    async def awaitable1():
        result = await future
        return "awaitable1", result

    async def awaitable2():
        result = await create_task(awaitable1())
        return "awaitable2", result

    task = create_task(awaitable2())
    weechat_task_cb(future.id, "data")

    assert not slack.active_tasks
    assert slack.active_responses == {
        task.id: ("awaitable2", ("awaitable1", ("data",)))
    }


def test_run_two_tasks_concurrently():
    slack.active_tasks = {}
    slack.active_responses = {}
    future1 = Future[str]()
    future2 = Future[str]()

    async def awaitable(future: Future[str]):
        result = await future
        return "awaitable", result

    task1 = create_task(awaitable(future1))
    task2 = create_task(awaitable(future2))
    weechat_task_cb(future1.id, "data1")
    weechat_task_cb(future2.id, "data2")

    assert not slack.active_tasks
    assert slack.active_responses == {
        task1.id: ("awaitable", ("data1",)),
        task2.id: ("awaitable", ("data2",)),
    }
