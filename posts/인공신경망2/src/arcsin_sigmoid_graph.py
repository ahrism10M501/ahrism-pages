import os
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.gridspec as gridspec

# 저장할 디렉토리 생성 (오류 방지)
os.makedirs("./graph", exist_ok=True)

# 다크 테마 설정
plt.style.use('dark_background')

# 커스텀 색상 정의
C_RED = '#FF3333'
C_MAGENTA = '#FF00FF'
C_DEEPBLUE = '#1F51FF'

# 공통 함수 정의
def sigmoid(z):
    return 1 / (1 + np.exp(-z))

# ==========================================
# 1. Sigmoid Input/Output Projection
# ==========================================
y_val = np.linspace(-7, 7, 500)
sig_val = sigmoid(y_val)

t = np.linspace(0, 2*np.pi, 500)
sin_input = 4 * np.sin(t) 
distorted_output = sigmoid(sin_input)

fig = plt.figure(figsize=(10, 8))
gs = gridspec.GridSpec(2, 2, width_ratios=[1, 1.2], height_ratios=[1.2, 1])

# 중앙 활성화 함수 (Top-Left)
ax_main = plt.subplot(gs[0, 0])
ax_main.plot(y_val, sig_val, color=C_MAGENTA, linewidth=2)
ax_main.set_title("Activation: $\sigma(z)$", fontsize=12)
ax_main.grid(True, alpha=0.2)

# 아래 입력 정현파 (Bottom-Left)
ax_in = plt.subplot(gs[1, 0])
ax_in.plot(sin_input, t, color=C_DEEPBLUE, alpha=0.8, linewidth=2)
ax_in.invert_yaxis() 
ax_in.set_xlabel("Input Amplitude ($z$)")
ax_in.set_ylabel("Time / Phase")
ax_in.set_title("Input Signal (Sine)", fontsize=10)
ax_in.grid(True, alpha=0.2)

# 우측 왜곡된 결과 (Top-Right)
ax_out = plt.subplot(gs[0, 1])
ax_out.plot(t, distorted_output, color=C_RED, linewidth=2)
ax_out.set_ylabel("Output $\sigma(z)$")
ax_out.set_xlabel("Time / Phase")
ax_out.set_title("Distorted Output (Non-linear)", fontsize=10)
ax_out.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig("./graph/asrsin_sigmoids.png")
plt.show()

# ==========================================
# 2. XOR Problem
# ==========================================
x_xor = np.array([[0,0], [1,1], [0,1], [1,0]])
y_xor = np.array([0, 0, 1, 1]) 

plt.figure(figsize=(6, 5))

# 데이터 포인트 (다크 테마에 맞게 색상 변경)
plt.scatter(x_xor[y_xor==0, 0], x_xor[y_xor==0, 1], c=C_DEEPBLUE, edgecolors='white', s=200, label='Class 0 (False)')
plt.scatter(x_xor[y_xor==1, 0], x_xor[y_xor==1, 1], c=C_MAGENTA, edgecolors='white', s=200, label='Class 1 (True)')

# 실패하는 선형 모델의 예시들
x_line = np.linspace(-0.5, 1.5, 10)
plt.plot(x_line, 0.5 - 0*x_line, color=C_RED, linestyle='--', alpha=0.6, label='Linear Attempt 1')
plt.plot(x_line, 1.2 - 1*x_line, color=C_RED, linestyle=':', alpha=0.8, label='Linear Attempt 2')

plt.title("XOR Problem: Impossible to Separate with One Line", fontsize=13)
plt.xlabel("Input $x_1$")
plt.ylabel("Input $x_2$")
plt.legend(loc='upper right', bbox_to_anchor=(1.45, 1))
plt.grid(True, linestyle=':', alpha=0.3)
plt.xlim(-0.2, 1.2)
plt.ylim(-0.2, 1.2)
plt.tight_layout()
plt.savefig("./graph/xor_graph.png")
plt.show()

# ==========================================
# 3. Sigmoid vs Clipped Sine Waves (3x2)
# ==========================================
x_pos = np.linspace(-5, 5, 500)

params = [
    {"A": 5, "f": 7,  "phi": 0,      "title": "High Amp & Freq"},
    {"A": 2, "f": 10, "phi": np.pi/4, "title": "Phase Shifted (pi/4)"},
    {"A": 10, "f": 3, "phi": 0,      "title": "Large Amp, Low Freq"},
    {"A": 1, "f": 15, "phi": -np.pi/2, "title": "Small Amp, High Freq"},
    {"A": 7, "f": 5,  "phi": np.pi,   "title": "Phase Shifted (pi)"},
    {"A": 3, "f": 2,  "phi": 0,      "title": "Low Amp & Freq"}
]

fig, axes = plt.subplots(3, 2, figsize=(10, 10), constrained_layout=True)
axes = axes.flatten()

for i, p in enumerate(params):
    A, f, phi = p["A"], p["f"], p["phi"]
    sine_wave = A * np.sin(f * x_pos + phi)
    
    # 이중 y축 적용 (잘림 현상 방지)
    ax1 = axes[i]
    ax2 = ax1.twinx()
    
    # 시그모이드 적용 그래프 (ax1, 0~1 스케일)
    line1 = ax1.plot(x_pos, sigmoid(sine_wave), color=C_MAGENTA, 
                     label=fr"$\sigma({A}\sin({f}x + \phi))$")[0]
    
    # 클리핑된 사인 그래프 (ax2, 원래 진폭 스케일)
    y_clipped = np.maximum(sine_wave, -0.5)
    line2 = ax2.plot(x_pos, y_clipped, color=C_DEEPBLUE, 
                     label=f"Clipped {A}sin(x)", linestyle="--", alpha=0.7)[0]
    
    ax1.set_title(p["title"])
    ax1.set_ylim(-0.1, 1.1) 
    ax1.grid(True, linestyle=':', alpha=0.3)
    
    # 범례 합치기
    ax1.legend(handles=[line1, line2], fontsize='small', loc='upper right')

fig.suptitle("Sigmoid vs Clipped Sine Waves (Various Parameters)", fontsize=16)
plt.savefig("./graph/asrsin_sigmoid_3x2.png")
plt.show()

# ==========================================
# 4. Neural Network Output Layer (이중 y축 수정)
# ==========================================
total_sine_sum = np.zeros_like(x_pos)
for p in params:
    total_sine_sum += p["A"] * np.sin(p["f"] * x_pos + p["phi"])

activated_output = sigmoid(total_sine_sum)

fig, ax1 = plt.subplots(figsize=(12, 6))

# 오른쪽 y축 생성 (합산된 원본 신호용)
ax2 = ax1.twinx()

# 합산된 사인파 (오른쪽 축)
line_sum = ax2.plot(x_pos, total_sine_sum, label="Summed Signal", 
                    color=C_DEEPBLUE, alpha=0.6, linestyle='--')[0]

# 시그모이드 통과 후 최종 출력 (왼쪽 축)
line_out = ax1.plot(x_pos, activated_output, label=r"Final Output: $\sigma(\sum)$", 
                    color=C_MAGENTA, linewidth=2)[0]

# -0.5 클리핑 라인 역할을 하는 임계값 표시
line_thresh = ax1.axhline(0.5, color=C_RED, linestyle=':', label="Threshold (0.5)")

plt.title("Neural Network Output Layer: Summation & Activation", fontsize=14)
ax1.set_xlabel("Input (x)")
ax1.set_ylabel("Final Output Probability (0 to 1)", color=C_MAGENTA)
ax2.set_ylabel("Summed Signal Amplitude", color=C_DEEPBLUE)

ax1.grid(True, which='both', linestyle='--', alpha=0.3)

# 범례 통합
ax1.legend(handles=[line_out, line_sum, line_thresh], loc="upper right")

plt.savefig("./graph/neural_output_sum.png")
plt.show()

# ==========================================
# 5. Multiple Distorted Signals (Hump)
# ==========================================
x = np.linspace(-10, 10, 1000)

z1 = sigmoid(2*x + 8)   
z2 = sigmoid(-2*x + 8)  
z3 = sigmoid(1.5*x - 2) 

combined = z1 + z2 - 1.2 

plt.figure(figsize=(10, 6))
plt.plot(x, z1, color=C_DEEPBLUE, linestyle='--', alpha=0.8, label="Neuron 1")
plt.plot(x, z2, color=C_MAGENTA, linestyle='--', alpha=0.8, label="Neuron 2")
plt.plot(x, combined, color=C_RED, linewidth=3, label="Final Combined Layer")

plt.fill_between(x, combined, alpha=0.2, color=C_RED)
plt.title("How Multiple Distorted Signals Create a 'Hump'", fontsize=14)
plt.axhline(0.5, color='white', linestyle=':', alpha=0.5, label="Threshold")
plt.legend()
plt.grid(True, alpha=0.2)
plt.tight_layout()
plt.show()