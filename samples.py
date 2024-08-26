import random
from time import sleep

from tiny_prob import TinyProb, SetConfig, capture_all

SetConfig(open_browser=False, ask_before_exit=True)


@TinyProb.capture_all
class TestApp1:
    p_value: int = 55

    def cycle(self):
        sleep(5)
        self.p_value = (self.p_value + 1) % 10
        print(">" * 24, f"[POST] Setting value to {self.p_value}")


@TinyProb.capture("b_value", "c_value")
class TestApp2:
    a_value: int = 10
    b_value: int = 20
    c_value: str = "Hello"
    d_value: dict = {"a": 1, "b": 2, "c": 3}

    def some_function(self):
        self.a_value = (self.a_value + 1) % 10
        self.b_value = (self.b_value + 1) % 10
        self.c_value = self.c_value[::-1]
        self.d_value["a"] = (self.d_value["a"] + 2) % 10
        self.d_value["b"] = (self.d_value["b"] + 3) % 10
        self.d_value["c"] = (self.d_value["c"] + 4) % 10


class TestApp3:
    @TinyProb.prob
    def debug_prob(self) -> int:
        x = random.randint(0, 100)
        print("I have been called {x} number of times!")
        return x


class TestApp4:
    static_prob = TinyProb.StaticProb("static_prob1")

    def cycle(self):
        print("TestApp4 cycle. Waiting for 10 seconds for static prob")
        self.static_prob.wait(10)
        self.static_prob.reset()
        print("TestApp4 mid-cycle")
        sleep(5)
        if self.static_prob.is_active():
            print("TestApp4 cycle end")
            return
        raise Exception("TestApp4 cycle not ended")





if __name__ == "__main__":
    ---------------------------------------------------------------------------------------------
    with TinyProbCore(open_browser=False, ask_before_exit=True) as tp:
        tp.add_pin("a", 1)
        # Then you can use `curl http://127.0.0.1:8080/all_pins` to see the result


    ---------------------------------------------------------------------------------------------
    with TinyProbCore(open_browser=False, ask_before_exit=True) as tp:
        import logging
        logger = logging.getLogger("tiny_prob")

        logger.addHandler(tp.get_log_handler())

        logger.error("Starting TinyProb -> Error")
        logger.warning("Starting TinyProb -> Warning")
        logger.info("Starting TinyProb ->  INFO")


    ---------------------------------------------------------------------------------------------
    with TinyProbCore(open_browser=False) as tp:
        getter, _ = tp.add_pin("var", 10)

        for i in range(10):
            print("var:", getter())
            sleep(1)

    ---------------------------------------------------------------------------------------------
    with TinyProbCore(open_browser=False, ask_before_exit=True) as tp:
        ev = tp.add_event_pin("event1")
        ev += lambda: print("Event 1 triggered")
        ev += lambda x: print(f"Event 1 triggered with value {x}")

    ---------------------------------------------------------------------------------------------
    with TinyProbCore(open_browser=False, ask_before_exit=True) as tp:
        prob = tp.add_debug_prob("event1")
        prob.wait()
        print("Continuing after event 1")

    ---------------------------------------------------------------------------------------------

    app1 = TestApp1()
    app2 = TestApp2()
    app3 = TestApp3()
    app4 = TestApp4()

    TinyProb.add_prob("restart_ui", lambda: TinyProb.send_command("restart_ui"), tooltip="Click me to restart UI!")

    for i in range(10):
        app1.cycle()
        app2.some_function()
        app3.debug_prob()
        app4.cycle()

    @capture_all
    class MyClass:
        a: int = 10

        def cycle(self):
            self.a = (self.a + 1) % 10
            print(">>", f"Setting value to {self.a}")

    with TinyProb() as tp:
        my_class = MyClass()

        for _ in range(100000):
            my_class.cycle()
            sleep(1)