from time import sleep

from tiny_prob import TinyProb


@TinyProb.capture_all
class TestApp:
    p_value: int = 55

    def cycle(self):
        sleep(5)
        self.p_value = (self.p_value + 1) % 10
        print(">" * 24, f"[POST] Setting value to {ta.p_value}")


if __name__ == "__main__":
    TinyProb.instance().start(open_browser=False)

    ta = TestApp()
    for i in range(10):
        print(">" * 10, f"[PRE] Setting value to {ta.p_value}")
        ta.cycle()

    TinyProb.instance().stop()
