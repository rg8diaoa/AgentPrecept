"""向后兼容 stub — 实际逻辑已移到 agentprecept.sync_graph"""
from agentprecept.sync_graph import *

if __name__ == "__main__":
    import sys
    sys.modules["__main__"].main()
