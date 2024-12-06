from . import Node

class MemoryInterruptNode(Node):
    """
    A MemoryInterrupt object is used to interrupt memory during a workflow.
    """
    
    def __init__(self, title, desc, interrupt_retrieval_memory, interrupt_conversation_memory, flow_data):
        """
        Initializes a MemoryInterrupt object.
        """
        super().__init__(
            "memory_interrupt",
            title=title,
            desc=desc,
            interrupt_retrieval_memory=interrupt_retrieval_memory,
            interrupt_conversation_memory=interrupt_conversation_memory,
            flow_data=flow_data
        )