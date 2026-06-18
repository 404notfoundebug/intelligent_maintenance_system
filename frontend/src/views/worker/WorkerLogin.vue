<template>
  <div class="login-page worker-login">
    <div class="login-card">
      <div class="login-header">
        <el-icon :size="48" color="#67c23a"><Tools /></el-icon>
        <h2>维修工人端登录</h2>
        <p>智能电梯扶梯维保系统 · 现场工作台</p>
      </div>
      <el-form ref="formRef" :model="form" :rules="rules" size="large" @submit.prevent="handleLogin">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" :prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" :prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="success" native-type="submit" :loading="loading" style="width:100%">
            登 录
          </el-button>
        </el-form-item>
      </el-form>
      <div class="login-footer">
        <el-button link @click="$router.push('/admin/login')">切换到管理员端</el-button>
        <el-button link @click="$router.push('/')">返回首页</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Tools } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const result = await userStore.login({ username: form.username, password: form.password })
    if (result.role !== 'worker') {
      ElMessage.warning('该账号不是维修工人，请使用工人账号登录')
      userStore.logout()
      return
    }
    ElMessage.success('登录成功')
    router.push('/worker/dashboard')
  } catch (err) {
    ElMessage.error(err?.response?.data?.detail || err?.response?.data?.message || '网络或服务异常')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 50%, #40916c 100%);
}

.worker-login .login-card {
  width: 400px;
  background: #fff;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-header h2 {
  margin: 12px 0 6px;
  font-size: 1.5rem;
  color: #303133;
}

.login-header p {
  margin: 0;
  color: #909399;
  font-size: 0.9rem;
}

.login-footer {
  display: flex;
  justify-content: center;
  gap: 12px;
}
</style>
