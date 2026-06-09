"""向后兼容 stub — 实际逻辑已移到 agentprecept.basic_audit"""
from agentprecept.basic_audit import main

if __name__ == "__main__":
    import sys
    sys.argv[0] = __file__
    main()
