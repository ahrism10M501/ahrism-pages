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

# 데이터 설정 (입력 x1, x2)
X = np.array([[0,0], [0,1], [1,0], [1,1]])
y_and = np.array([0, 0, 0, 1]) # AND 출력
y_or  = np.array([0, 1, 1, 1]) # OR 출력

def draw_logic_gate(title, X, y, filename, boundary_eq):
    """
    진리표, 기본 그래프, 직선이 추가된 그래프를 1x3 서브플롯으로 그리는 함수
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), constrained_layout=True)
    
    # --------------------------------------------------
    # 1. 진리표 (Truth Table)
    # --------------------------------------------------
    ax_table = axes[0]
    ax_table.axis('off')
    
    # 테이블 데이터 준비
    cell_text = []
    for i in range(4):
        cell_text.append([str(X[i][0]), str(X[i][1]), str(y[i])])
    
    columns = ('Input 1', 'Input 2', 'Output')
    
    # 테이블 생성 및 스타일링
    table = ax_table.table(cellText=cell_text, colLabels=columns, loc='center', cellLoc='center')
    table.scale(1, 2.5) # 테이블 크기 조절
    
    # 폰트 크기 강제 지정 해제 후 설정
    table.auto_set_font_size(False)
    table.set_fontsize(14)
    
    # 헤더 및 셀 색상 조정 (다크 테마에 맞게)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor('gray')
        cell.set_facecolor('black') # 기본 배경을 검은색으로 명시
        
        if row == 0:
            # 헤더 행
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor('#333333')
        else:
            # 데이터 행
            if col == 2:
                # 출력값에 따라 텍스트 색상 변경 (0: 딥블루, 1: 마젠타)
                if cell_text[row-1][2] == '0':
                    cell.set_text_props(color=C_DEEPBLUE, weight='bold')
                else:
                    cell.set_text_props(color=C_MAGENTA, weight='bold')
            else:
                # 입력값(숫자)이 잘 보이도록 흰색으로 명시적 지정
                cell.set_text_props(color='white')
                    
    ax_table.set_title(f"[{title} Truth Table]", fontsize=14, pad=20, color='white')

    # --------------------------------------------------
    # 2. 기본 그래프 (Graph)
    # --------------------------------------------------
    ax_graph = axes[1]
    
    # 클래스별로 분리해서 그리기
    ax_graph.scatter(X[y==0, 0], X[y==0, 1], c=C_DEEPBLUE, edgecolors='white', s=200, label='Class 0')
    ax_graph.scatter(X[y==1, 0], X[y==1, 1], c=C_MAGENTA, edgecolors='white', s=200, label='Class 1')
    
    ax_graph.set_title(f"[{title} Graph]", fontsize=14)
    ax_graph.set_xlim(-0.5, 1.5)
    ax_graph.set_ylim(-0.5, 1.5)
    ax_graph.set_xlabel("Input 1")
    ax_graph.set_ylabel("Input 2")
    ax_graph.grid(True, linestyle=':', alpha=0.3)
    ax_graph.legend(loc='upper left')

    # --------------------------------------------------
    # 3. 모델을 나타내는 직선이 추가된 그래프 (Graph + Model)
    # --------------------------------------------------
    ax_model = axes[2]
    
    # 데이터 포인트 다시 그리기
    ax_model.scatter(X[y==0, 0], X[y==0, 1], c=C_DEEPBLUE, edgecolors='white', s=200, zorder=3)
    ax_model.scatter(X[y==1, 0], X[y==1, 1], c=C_MAGENTA, edgecolors='white', s=200, zorder=3)
    
    # 결정 경계 직선 그리기
    x_line = np.linspace(-0.5, 1.5, 100)
    y_line = boundary_eq(x_line)
    
    ax_model.plot(x_line, y_line, color=C_RED, linestyle='--', linewidth=2, label='Model Boundary', zorder=2)
    
    # 영역 색칠 (배경색으로 영역 구분)
    ax_model.fill_between(x_line, y_line, 1.5, color=C_MAGENTA, alpha=0.1, zorder=1)
    ax_model.fill_between(x_line, -0.5, y_line, color=C_DEEPBLUE, alpha=0.1, zorder=1)
    
    ax_model.set_title(f"[{title} Graph + Model]", fontsize=14)
    ax_model.set_xlim(-0.5, 1.5)
    ax_model.set_ylim(-0.5, 1.5)
    ax_model.set_xlabel("Input 1")
    ax_model.grid(True, linestyle=':', alpha=0.3)
    ax_model.legend(loc='upper left')

    # 저장 및 출력
    fig.suptitle(f"{title} Gate Classification", fontsize=18, fontweight='bold', y=1.05)
    plt.savefig(f"./graph/{filename}.png", bbox_inches='tight')
    plt.show()

# ==========================================
# 실행
# ==========================================

# 1. AND 게이트: 결정 경계선 y = -x + 1.5
def and_boundary(x):
    return -x + 1.5

draw_logic_gate("AND", X, y_and, "and_gate_visualization", and_boundary)

# 2. OR 게이트: 결정 경계선 y = -x + 0.5
def or_boundary(x):
    return -x + 0.5

draw_logic_gate("OR", X, y_or, "or_gate_visualization", or_boundary)