<template>
  <div class="login-page">
    <div class="login-panel">
      <section class="login-hero">
        <div class="system-badge">Elevator & Escalator Maintenance</div>
        <h1>面向电梯扶梯维保场景的多模态知识检索与标准化作业辅助系统</h1>
        <p>知识检索、RAG 检修建议、点检工单、故障上报与维保记录一体化管理。</p>
      </section>

      <section class="login-form-wrap">
        <h2>用户登录</h2>
        <p class="form-tip">请输入账号密码进入后台管理系统</p>
        <el-form ref="formRef" :model="form" :rules="rules" class="login-form" @keyup.enter="handleLogin">
          <el-form-item prop="username">
            <el-input v-model="form.username" size="large" placeholder="用户名" prefix-icon="User" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              size="large"
              placeholder="密码"
              type="password"
              show-password
              prefix-icon="Lock"
            />
          </el-form-item>
          <el-button class="login-button" type="primary" size="large" :loading="loading" @click="handleLogin">
            登录系统
          </el-button>
        </el-form>
      </section>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../../stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: 'admin',
  password: 'admin123456'
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
    await userStore.login({ ...form })
    ElMessage.success('登录成功')
    const redirect = route.query.redirect ? decodeURIComponent(route.query.redirect) : '/dashboard'
    router.replace(redirect)
  } catch {
    // request interceptor displays the error message
  } finally {
    loading.value = false
  }
}
</script>
