import os
import matplotlib.pyplot as plt
import numpy as np

# 저장할 디렉토리 생성
os.makedirs("./graph", exist_ok=True)

# 다크 테마 및 커스텀 색상 설정
plt.style.use('dark_background')
C_RED = '#FF3333'
C_MAGENTA = '#FF00FF'
C_DEEPBLUE = '#1F51FF'

# 데이터 설정 (XOR 입력 및 출력)
X = np.array([[0,0], [0,1], [1,0], [1,1]])
y_xor = np.array([0, 1, 1, 0])

fig, axes = plt.subplots(1, 3, figsize=(15, 5), constrained_layout=True)

# --------------------------------------------------
# 1. 진리표 (Truth Table)
# --------------------------------------------------
ax_table = axes[0]
ax_table.axis('off')

cell_text = []
for i in range(4):
    cell_text.append([str(X[i][0]), str(X[i][1]), str(y_xor[i])])

columns = ('Input 1', 'Input 2', 'Output')

table = ax_table.table(cellText=cell_text, colLabels=columns, loc='center', cellLoc='center')
table.scale(1, 2.5) 
table.auto_set_font_size(False)
table.set_fontsize(14)

for (row, col), cell in table.get_celld().items():
    cell.set_edgecolor('gray')
    cell.set_facecolor('black') 
    
    if row == 0:
        cell.set_text_props(weight='bold', color='white')
        cell.set_facecolor('#333333')
    else:
        if col == 2:
            if cell_text[row-1][2] == '0':
                cell.set_text_props(color=C_DEEPBLUE, weight='bold')
            else:
                cell.set_text_props(color=C_MAGENTA, weight='bold')
        else:
            cell.set_text_props(color='white')
                
ax_table.set_title("[XOR Truth Table]", fontsize=14, pad=20, color='white')

# --------------------------------------------------
# 2. 기본 그래프 (Graph)
# --------------------------------------------------
ax_graph = axes[1]

ax_graph.scatter(X[y_xor==0, 0], X[y_xor==0, 1], c=C_DEEPBLUE, edgecolors='white', s=200, label='Class 0')
ax_graph.scatter(X[y_xor==1, 0], X[y_xor==1, 1], c=C_MAGENTA, edgecolors='white', s=200, label='Class 1')

ax_graph.set_title("[XOR Graph]", fontsize=14)
ax_graph.set_xlim(-0.5, 1.5)
ax_graph.set_ylim(-0.5, 1.5)
ax_graph.set_xlabel("Input 1")
ax_graph.set_ylabel("Input 2")
ax_graph.grid(True, linestyle=':', alpha=0.3)
ax_graph.legend(loc='upper left')

# --------------------------------------------------
# 3. 모델을 나타내는 직선(선형 경계)의 실패 예시
# --------------------------------------------------
ax_model = axes[2]

# 데이터 포인트 그리기 (zorder를 높여 선 위에 표시되도록 함)
ax_model.scatter(X[y_xor==0, 0], X[y_xor==0, 1], c=C_DEEPBLUE, edgecolors='white', s=200, zorder=3, label='Class 0')
ax_model.scatter(X[y_xor==1, 0], X[y_xor==1, 1], c=C_MAGENTA, edgecolors='white', s=200, zorder=3, label='Class 1')

# 분류에 실패하는 5가지 직선(선형 모델) 예시 생성
x_vals = np.linspace(-0.5, 1.5, 100)

# Line 1: 가로선
ax_model.plot(x_vals, [0.5]*100, color=C_RED, linestyle='--', alpha=0.6, label='Attempt 1')
# Line 2: 세로선
ax_model.plot([0.5]*100, x_vals, color=C_RED, linestyle='-.', alpha=0.6, label='Attempt 2')
# Line 3: 대각선 1
ax_model.plot(x_vals, x_vals - 0.5, color=C_RED, linestyle=':', alpha=0.7, label='Attempt 3')
# Line 4: 대각선 2
ax_model.plot(x_vals, -x_vals + 1.5, color=C_RED, dashes=[10, 5, 2, 5], alpha=0.6, label='Attempt 4')
# Line 5: 완만한 기울기
ax_model.plot(x_vals, 0.3 * x_vals + 0.35, color=C_RED, linestyle='-', alpha=0.4, label='Attempt 5')

ax_model.set_title("[XOR can't classify Linear]", fontsize=14)
ax_model.set_xlim(-0.5, 1.5)
ax_model.set_ylim(-0.5, 1.5)
ax_model.set_xlabel("Input 1")
ax_model.grid(True, linestyle=':', alpha=0.3)
ax_model.legend(loc='upper left', fontsize=9)

# 저장 및 출력
fig.suptitle("XOR Gate: The Limitation of Linear Models", fontsize=18, fontweight='bold', y=1.05)
plt.savefig("./graph/xor_gate_linear_failure.png", bbox_inches='tight')
plt.show()