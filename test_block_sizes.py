from dynamic_maze import DynamicMaze

print("EASY:")
m_easy = DynamicMaze(width=15, height=15)
print(f"Size: {max(m_easy.width, m_easy.height)}")
print(f"Block Size: {m_easy.block_size}")

print("\nMEDIUM:")
m_med = DynamicMaze(width=20, height=20)
print(f"Size: {max(m_med.width, m_med.height)}")
print(f"Block Size: {m_med.block_size}")

print("\nHARD:")
m_hard = DynamicMaze(width=25, height=25)
print(f"Size: {max(m_hard.width, m_hard.height)}")
print(f"Block Size: {m_hard.block_size}")
