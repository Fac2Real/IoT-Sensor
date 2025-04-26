import service.simulation.simulateTest as simulator
if __name__ == "__main__":
    # python -u simulateTest.py --count 10 --interval 1 --simulator temp
    # python -u simulateTest.py --count 10 --interval 1 --simulator humidity
    # python -u simulateTest.py --count 10 --interval 1 --simulator humidity_temp
    simulator.main()
    
