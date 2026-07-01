<template>
  <div class="entry-page">
    <!-- 第二层：弥散光晕（巨大模糊彩色光晕，有呼吸动画） -->
    <div class="bg-aura aura-blue"></div>
    <div class="bg-aura aura-purple"></div>
    <div class="bg-aura aura-amber"></div>
    <div class="bg-aura aura-cyan"></div>

    <!-- 第三层：网格点阵纹理 -->
    <div class="bg-texture"></div>

    <!-- 左上角品牌标识 -->
    <div class="top-brand">
      <div class="top-brand-dot"></div>
      <span class="top-brand-text">梯小维</span>
    </div>

    <!-- 主体布局 -->
    <div class="main-container">
      <!-- 左侧：品牌展示区 -->
      <div class="brand-section">
        <div class="brand-inner">
          <!-- 电梯 SVG 展示 -->
          <div class="elevator-showcase">
            <!-- 悬浮光环 -->
            <div class="elevator-halo"></div>
            <svg viewBox="0 0 220 380" class="elevator-svg" xmlns="http://www.w3.org/2000/svg">
              <!-- 光晕背景 -->
              <ellipse cx="110" cy="190" rx="100" ry="160" fill="url(#elevGlow)" opacity="0.5" />
              <!-- 井道 -->
              <rect x="60" y="20" width="100" height="330" rx="12" fill="none" stroke="#CBD5E1" stroke-width="1.5" />
              <!-- 楼层线 -->
              <line v-for="n in 7" :key="n" x1="60" :y1="22 + n * 45" x2="160" :y2="22 + n * 45" stroke="#E2E8F0" stroke-width="0.8" stroke-dasharray="5 4" />
              <!-- 楼层数字 -->
              <text v-for="n in 7" :key="'f'+n" x="50" :y1="27 + n * 45" :y="27 + n * 45" text-anchor="end" fill="#94A3B8" font-size="11" font-family="monospace" font-weight="300">{{ 8-n }}F</text>
              <!-- 电梯轿厢（浮动动画） -->
              <g class="elevator-cabin">
                <rect x="76" y="200" width="68" height="72" rx="7" fill="rgba(37,99,235,0.04)" stroke="#2563EB" stroke-width="1.5" />
                <rect x="83" y="208" width="54" height="56" rx="4" fill="rgba(37,99,235,0.03)" />
                <!-- 楼层指示 -->
                <rect x="122" y="213" width="16" height="11" rx="2.5" fill="rgba(37,99,235,0.12)" />
                <text x="130" y="221" text-anchor="middle" fill="#2563EB" font-size="8" font-weight="600" font-family="monospace">4</text>
                <!-- 导轨 -->
                <line x1="94" y1="216" x2="94" y2="264" stroke="rgba(37,99,235,0.15)" stroke-width="1" />
                <line x1="126" y1="216" x2="126" y2="264" stroke="rgba(37,99,235,0.15)" stroke-width="1" />
              </g>
              <!-- 钢丝绳 -->
              <line x1="108" y1="10" x2="108" y2="200" stroke="#CBD5E1" stroke-width="0.8" />
              <line x1="112" y1="10" x2="112" y2="200" stroke="#E2E8F0" stroke-width="0.6" />
              <!-- 曳引机 -->
              <rect x="92" y="2" width="36" height="16" rx="6" fill="none" stroke="#CBD5E1" stroke-width="1.2" />
              <circle cx="110" cy="10" r="4.5" fill="none" stroke="#94A3B8" stroke-width="0.8" />
              <!-- 缓冲器 -->
              <rect x="100" y="352" width="20" height="7" rx="3" fill="none" stroke="#E2E8F0" stroke-width="1" />
              <!-- 连接线装饰 -->
              <path d="M170,100 Q180,120 175,150" fill="none" stroke="#93C5FD" stroke-width="1" stroke-dasharray="3 5" opacity="0.4" />
              <path d="M170,230 Q180,250 175,280" fill="none" stroke="#93C5FD" stroke-width="1" stroke-dasharray="3 5" opacity="0.4" />
              <!-- 数据小圆点 -->
              <circle cx="175" cy="100" r="2.5" fill="#2563EB" opacity="0.25">
                <animate attributeName="opacity" values="0.1;0.35;0.1" dur="3s" repeatCount="indefinite" />
              </circle>
              <circle cx="175" cy="280" r="2" fill="#2563EB" opacity="0.2">
                <animate attributeName="opacity" values="0.05;0.3;0.05" dur="4s" repeatCount="indefinite" />
              </circle>
              <defs>
                <radialGradient id="elevGlow" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stop-color="#2563EB" stop-opacity="0.08" />
                  <stop offset="100%" stop-color="#2563EB" stop-opacity="0" />
                </radialGradient>
              </defs>
            </svg>
          </div>

          <!-- 标语文字 -->
          <div class="brand-copy">
            <p class="brand-headline">AI 驱动的预测性维护</p>
            <p class="brand-desc">让每一次检修都有据可依</p>
          </div>
        </div>
      </div>

      <!-- 右侧：登录面板区 -->
      <div class="login-section">
        <div class="login-wrapper">
          <!-- 面板切换：mode="out-in" 确保旧面板完全离开后新面板才进入 -->
          <Transition name="panel-switch" mode="out-in">
            <!-- 角色选择卡片 -->
            <div v-if="!loginVisible" key="role" class="login-card">
              <h2 class="card-title">登录梯小维</h2>
              <p class="card-desc">选择您的身份以进入对应平台</p>

              <button class="role-btn role-admin" @click="openLogin('admin')">
                <span class="role-icon">
                  <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8">
                    <rect x="3" y="4" width="18" height="13" rx="2" />
                    <path d="M7 20h10M12 16v4" />
                  </svg>
                </span>
                <span class="role-body">
                  <strong>管理员端</strong>
                  <small>设备管理 · 数据监控 · 系统配置</small>
                </span>
                <svg class="role-arrow" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6" /></svg>
              </button>

              <button class="role-btn role-worker" @click="openLogin('worker')">
                <span class="role-icon">
                  <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8">
                    <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" />
                  </svg>
                </span>
                <span class="role-body">
                  <strong>维修工人端</strong>
                  <small>故障上报 · 工单执行 · 知识查询</small>
                </span>
                <svg class="role-arrow" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6" /></svg>
              </button>

              <p class="card-footer">安全 · 高效 · 智能</p>
            </div>

            <!-- 登录表单卡片 -->
            <div v-else key="login" class="login-card">
              <div class="login-header">
                <button class="back-btn" @click="loginVisible = false">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 18l-6-6 6-6" /></svg>
                </button>
                <h3 class="login-title">{{ loginRole === 'admin' ? '管理员登录' : '维修工人登录' }}</h3>
              </div>

              <el-form
                ref="loginFormRef"
                :model="loginForm"
                :rules="loginRules"
                label-position="top"
                size="large"
                @keyup.enter="handleLogin"
              >
                <el-form-item label="用户名" prop="username">
                  <el-input
                    v-model="loginForm.username"
                    placeholder="请输入用户名"
                    :prefix-icon="UserIcon"
                    autofocus
                  />
                </el-form-item>
                <el-form-item label="密码" prop="password">
                  <el-input
                    v-model="loginForm.password"
                    type="password"
                    placeholder="请输入密码"
                    :prefix-icon="LockIcon"
                    show-password
                  />
                </el-form-item>
                <el-form-item class="submit-item">
                  <el-button
                    type="primary"
                    size="large"
                    :loading="loginLoading"
                    @click="handleLogin"
                    class="submit-btn"
                  >
                    登 录
                  </el-button>
                </el-form-item>
              </el-form>
            </div>
          </Transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { User as UserIcon, Lock as LockIcon } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const loginVisible = ref(false)
const loginRole = ref('')
const loginLoading = ref(false)
const loginFormRef = ref(null)

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

function openLogin(role) {
  loginRole.value = role
  loginForm.username = ''
  loginForm.password = ''
  loginVisible.value = true
  nextTick(() => {
    loginFormRef.value?.resetFields()
  })
}

async function handleLogin() {
  if (!loginFormRef.value) return
  try {
    await loginFormRef.value.validate()
  } catch {
    return
  }

  loginLoading.value = true
  try {
    const result = await userStore.login({
      username: loginForm.username,
      password: loginForm.password
    })

    const actualRole = result.role
    loginVisible.value = false

    if (actualRole !== loginRole.value) {
      userStore.logout()
      ElMessage.warning(`您的角色是"${actualRole === 'admin' ? '管理员' : '维修工人'}"，与所选端不匹配，请重新选择`)
      return
    }

    ElMessage.success('登录成功')

    if (actualRole === 'admin') {
      router.push('/admin/dashboard')
    } else if (actualRole === 'worker') {
      router.push('/worker/dashboard')
    }
  } catch (err) {
    ElMessage.error(err?.message || '登录失败，请检查用户名和密码')
  } finally {
    loginLoading.value = false
  }
}
</script>

<style scoped>
/* ============================================
   整体页面 - 第一层：三色柔光渐变
   ============================================ */
.entry-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  /* 三色柔光渐变：浅蓝灰 → 淡蓝 → 淡紫粉 */
  background:
    linear-gradient(
      155deg,
      #F8FAFC 0%,
      #F0F4F8 20%,
      #E0F2FE 45%,
      #F0F4F8 65%,
      #F3E8FF 85%,
      #F8FAFC 100%
    );
  position: relative;
  overflow: hidden;
  font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', -apple-system, sans-serif;
  -webkit-font-smoothing: antialiased;
}

/* ============================================
   第二层：弥散光晕（4 个巨大模糊彩色光晕 + 呼吸动画）
   ============================================ */
.bg-aura {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
  z-index: 0;
}

/* 左上：淡蓝色光晕 */
.aura-blue {
  width: 620px;
  height: 620px;
  background: radial-gradient(circle, rgba(56, 189, 248, 0.09) 0%, rgba(56, 189, 248, 0.03) 45%, transparent 70%);
  top: -180px;
  left: -140px;
  filter: blur(80px);
  animation: auraBreatheBlue 10s ease-in-out infinite;
}

@keyframes auraBreatheBlue {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(40px, 20px) scale(1.08);
  }
  66% {
    transform: translate(-15px, -30px) scale(0.94);
  }
}

/* 右上：淡青色光晕 */
.aura-cyan {
  width: 480px;
  height: 480px;
  background: radial-gradient(circle, rgba(6, 182, 212, 0.06) 0%, rgba(6, 182, 212, 0.02) 40%, transparent 70%);
  top: -100px;
  right: -80px;
  filter: blur(70px);
  animation: auraBreatheCyan 8s ease-in-out infinite;
}

@keyframes auraBreatheCyan {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  50% {
    transform: translate(-30px, 25px) scale(1.1);
  }
}

/* 右下：淡紫色光晕 */
.aura-purple {
  width: 560px;
  height: 560px;
  background: radial-gradient(circle, rgba(167, 139, 250, 0.08) 0%, rgba(167, 139, 250, 0.03) 45%, transparent 70%);
  bottom: -160px;
  right: -100px;
  filter: blur(90px);
  animation: auraBreathePurple 11s ease-in-out infinite;
}

@keyframes auraBreathePurple {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(-50px, -15px) scale(1.06);
  }
  66% {
    transform: translate(20px, 20px) scale(0.92);
  }
}

/* 左下：极淡琥珀色光晕 */
.aura-amber {
  width: 420px;
  height: 420px;
  background: radial-gradient(circle, rgba(253, 230, 138, 0.05) 0%, rgba(253, 230, 138, 0.01) 50%, transparent 70%);
  bottom: -80px;
  left: -60px;
  filter: blur(75px);
  animation: auraBreatheAmber 9s ease-in-out infinite;
}

@keyframes auraBreatheAmber {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  50% {
    transform: translate(30px, -20px) scale(1.07);
  }
}

/* ============================================
   第三层：网格点阵纹理
   ============================================ */
.bg-texture {
  position: absolute;
  inset: 0;
  background-image: radial-gradient(rgba(148, 163, 184, 0.22) 0.8px, transparent 0.8px);
  background-size: 36px 36px;
  opacity: 0.5;
  pointer-events: none;
  z-index: 0;
}

/* ============================================
   左上角品牌标识
   ============================================ */
.top-brand {
  position: absolute;
  top: 32px;
  left: 40px;
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 2;
}

.top-brand-dot {
  width: 28px;
  height: 28px;
  border-radius: 9px;
  background: linear-gradient(135deg, #2563EB 0%, #38BDF8 100%);
  box-shadow: 0 10px 22px rgba(37, 99, 235, 0.18);
  flex-shrink: 0;
  position: relative;
}

.top-brand-dot::before,
.top-brand-dot::after {
  content: '';
  position: absolute;
  top: 7px;
  bottom: 7px;
  width: 3px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.92);
}

.top-brand-dot::before {
  left: 9px;
}

.top-brand-dot::after {
  right: 9px;
}

.top-brand-text {
  font-family: 'Microsoft YaHei UI', 'PingFang SC', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 1.18rem;
  font-weight: 700;
  line-height: 1;
  color: #102033;
  letter-spacing: 0.02em;
  text-shadow: 0 1px 0 rgba(255, 255, 255, 0.75);
}

/* ============================================
   主体容器
   ============================================ */
.main-container {
  position: relative;
  z-index: 1;
  display: flex;
  width: 100%;
  max-width: 1040px;
  min-height: 560px;
  margin: 0 40px;
  gap: 64px;
  animation: containerIn 0.7s cubic-bezier(0.22, 1, 0.36, 1) both;
}

@keyframes containerIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ============================================
   左侧：品牌展示区
   ============================================ */
.brand-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.brand-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0;
}

/* 电梯 SVG */
.elevator-showcase {
  position: relative;
}

/* 悬浮光环 */
.elevator-halo {
  position: absolute;
  width: 260px;
  height: 260px;
  border-radius: 50%;
  border: 1px solid rgba(37, 99, 235, 0.08);
  background: radial-gradient(circle, rgba(37, 99, 235, 0.03) 0%, rgba(37, 99, 235, 0.01) 50%, transparent 70%);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation: haloPulse 4s ease-in-out infinite;
  pointer-events: none;
}

@keyframes haloPulse {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.6;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.12);
    opacity: 1;
  }
}

.elevator-svg {
  width: 200px;
  height: auto;
  position: relative;
  z-index: 1;
}

.elevator-cabin {
  animation: cabinFloat 3s ease-in-out infinite;
}

@keyframes cabinFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-18px); }
}

/* 标语 */
.brand-copy {
  margin-top: 28px;
  text-align: center;
}

.brand-headline {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 400;
  color: #1E293B;
  letter-spacing: 0.03em;
  line-height: 1.7;
}

.brand-desc {
  margin: 4px 0 0;
  font-size: 0.9rem;
  font-weight: 300;
  color: #64748B;
  letter-spacing: 0.03em;
}

/* ============================================
   右侧：登录面板区
   ============================================ */
.login-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-wrapper {
  width: 100%;
  max-width: 400px;
  position: relative;
}

/* ============================================
   登录卡片 - 柔和漂浮阴影
   ============================================ */
.login-card {
  background: rgba(255, 255, 255, 0.65);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 18px;
  padding: 38px 34px;
  /* 立体漂浮阴影：大扩散 + 内顶部高光线 */
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.04),
    0 4px 12px rgba(0, 0, 0, 0.04),
    0 30px 80px -20px rgba(0, 40, 80, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

/* 卡片标题 */
.card-title {
  margin: 0 0 6px;
  font-size: 1.25rem;
  font-weight: 600;
  color: #0F172A;
  letter-spacing: 0.02em;
}

.card-desc {
  margin: 0 0 28px;
  font-size: 0.88rem;
  color: #64748B;
  font-weight: 400;
}

/* ============================================
   角色选择按钮
   ============================================ */
.role-btn {
  display: flex;
  align-items: center;
  gap: 14px;
  width: 100%;
  padding: 16px 18px;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
  text-align: left;
  color: #1E293B;
  margin-bottom: 12px;
}

.role-btn:last-of-type {
  margin-bottom: 0;
}

.role-btn:hover {
  transform: translateY(-2px);
}

.role-admin:hover {
  border-color: #93C5FD;
  box-shadow: 0 4px 16px rgba(37, 99, 235, 0.08);
  background: #FAFCFE;
}

.role-worker:hover {
  border-color: #86EFAC;
  box-shadow: 0 4px 16px rgba(34, 197, 94, 0.08);
  background: #FAFEFA;
}

.role-icon {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.role-admin .role-icon {
  background: #EFF6FF;
  color: #2563EB;
}

.role-worker .role-icon {
  background: #F0FDF4;
  color: #16A34A;
}

.role-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.role-body strong {
  font-size: 0.95rem;
  font-weight: 600;
  color: #1E293B;
}

.role-body small {
  font-size: 0.78rem;
  color: #94A3B8;
  font-weight: 400;
}

.role-arrow {
  color: #CBD5E1;
  flex-shrink: 0;
  transition: all 0.2s;
}

.role-btn:hover .role-arrow {
  color: #94A3B8;
  transform: translateX(3px);
}

/* 卡片底部文字 */
.card-footer {
  margin: 24px 0 0;
  text-align: center;
  font-size: 0.72rem;
  color: #CBD5E1;
  font-weight: 400;
  letter-spacing: 0.1em;
}

/* ============================================
   登录表单
   ============================================ */
.login-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 26px;
}

.back-btn {
  width: 30px;
  height: 30px;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  background: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #94A3B8;
  transition: all 0.2s;
  flex-shrink: 0;
}

.back-btn:hover {
  background: #F1F5F9;
  border-color: #CBD5E1;
  color: #475569;
  transform: translateY(-1px);
}

.login-title {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 600;
  color: #0F172A;
  letter-spacing: 0.02em;
}

/* Element Plus 表单覆盖 */
.login-card :deep(.el-form-item) {
  margin-bottom: 18px;
}

.login-card :deep(.el-form-item__label) {
  color: #475569 !important;
  font-weight: 500;
  font-size: 0.85rem;
  margin-bottom: 4px;
}

.login-card :deep(.el-input__wrapper) {
  background: #F8FAFC !important;
  border: 1px solid #E2E8F0 !important;
  border-radius: 10px !important;
  box-shadow: none !important;
  transition: all 0.2s ease;
}

.login-card :deep(.el-input__wrapper:hover) {
  border-color: #CBD5E1 !important;
  background: #FFFFFF !important;
}

.login-card :deep(.el-input__wrapper.is-focus) {
  border-color: #2563EB !important;
  background: #FFFFFF !important;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.08) !important;
}

.login-card :deep(.el-input__inner) {
  color: #1E293B !important;
}

.login-card :deep(.el-input__inner::placeholder) {
  color: #94A3B8 !important;
}

.login-card :deep(.el-input__prefix-inner) {
  color: #94A3B8 !important;
}

.login-card :deep(.el-input__suffix-inner) {
  color: #94A3B8 !important;
}

.submit-item {
  margin-top: 6px;
  margin-bottom: 0;
}

.submit-btn {
  width: 100%;
  height: 46px;
  font-size: 0.95rem;
  font-weight: 500;
  letter-spacing: 0.12em;
  border-radius: 10px;
  background: #2563EB !important;
  border: none !important;
  color: #FFFFFF !important;
  transition: all 0.2s ease !important;
  box-shadow: 0 1px 3px rgba(37, 99, 235, 0.12);
}

.submit-btn:hover {
  background: #1D4ED8 !important;
  box-shadow: 0 4px 16px rgba(37, 99, 235, 0.2) !important;
  transform: translateY(-1px);
}

.submit-btn:active {
  transform: translateY(0);
  box-shadow: 0 1px 2px rgba(37, 99, 235, 0.1) !important;
}

/* ============================================
   面板切换过渡动画
   ============================================ */
.panel-switch-enter-active {
  transition: all 0.4s cubic-bezier(0.22, 1, 0.36, 1);
}

.panel-switch-leave-active {
  transition: none;
}

.panel-switch-enter-from {
  opacity: 0;
  transform: translateY(16px) scale(0.98);
}

/* ============================================
   响应式
   ============================================ */
@media (max-width: 860px) {
  .top-brand {
    position: relative;
    top: auto;
    left: auto;
    padding: 24px 28px 0;
  }

  .main-container {
    flex-direction: column;
    gap: 36px;
    margin: 0 24px;
    min-height: auto;
    padding-bottom: 40px;
  }

  .brand-section {
    padding-top: 8px;
  }

  .elevator-svg {
    width: 140px;
  }

  .brand-headline {
    font-size: 1rem;
  }

  .login-wrapper {
    max-width: 100%;
  }

  .elevator-halo {
    width: 200px;
    height: 200px;
  }
}
</style>
