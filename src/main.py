from app.application import BacktestingEngine

def _configure_log():
    pass

if __name__ == "__main__":
    try:
        spx_bt = BacktestingEngine()
        spx_bt.run()
    except Exception as e:
        print(str(e))