"""向后兼容 stub — 实际逻辑已移到 agentprecept.basic_audit"""
from agentprecept.basic_audit import *

if __name__ == "__main__":
    import sys
    sys.modules["__main__"].main()
