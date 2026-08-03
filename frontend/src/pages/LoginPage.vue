<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NButton,
  NForm,
  NFormItem,
  NInput,
  useMessage,
} from 'naive-ui'
import { login } from '@/services/authService'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const message = useMessage()
const auth = useAuthStore()

const form = ref({ username: 'worker_demo', password: 'demo123456' })
const loading = ref(false)

async function handleLogin() {
  if (!form.value.username || !form.value.password) {
    message.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    const data = await login(form.value.username, form.value.password)
    auth.setAuth(data.access_token, data.user)
    message.success('登录成功')
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : null
    if (redirect) {
      router.push(redirect)
      return
    }
    // 角色分流：律师进工作台，管理员进后台，劳动者进首页
    if (data.user.role === 'lawyer') {
      router.push('/lawyer/dashboard')
    } else if (data.user.role === 'admin') {
      router.push('/admin/overview')
    } else {
      router.push('/')
    }
  } catch (error) {
    message.error(error instanceof Error ? error.message : '登录失败')
  } finally {
    loading.value = false
  }
}

function fillDemo(username: string) {
  form.value.username = username
  form.value.password = 'demo123456'
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card glass-card fade-in">
      <div class="auth-brand">
        <span class="auth-logo">⚖️</span>
        <h1>劳动维权平台</h1>
        <p>智能生成法律文书 · 连接专业律师</p>
      </div>

      <n-form :model="form" label-placement="top" size="large" @keyup.enter="handleLogin">
        <n-form-item label="用户名">
          <n-input v-model:value="form.username" placeholder="请输入用户名" />
        </n-form-item>
        <n-form-item label="密码">
          <n-input v-model:value="form.password" type="password" show-password-on="click" placeholder="请输入密码" />
        </n-form-item>
        <n-button type="primary" block size="large" :loading="loading" @click="handleLogin">
          登 录
        </n-button>
      </n-form>

      <div class="auth-footer">
        <span>还没有账号？</span>
        <n-button text type="primary" @click="router.push('/register')">立即注册</n-button>
      </div>

      <n-divider title-placement="left" style="font-size: 12px; color: var(--text-tertiary)">
        演示账号快捷填充
      </n-divider>
      <div class="demo-accounts">
        <n-button size="small" quaternary @click="fillDemo('worker_demo')">👷 劳动者演示账号</n-button>
        <n-button size="small" quaternary @click="fillDemo('lawyer01')">⚖️ 律师演示账号</n-button>
        <n-button size="small" quaternary @click="fillDemo('admin')">🛡️ 管理员演示账号</n-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: radial-gradient(1200px 600px at 20% 10%, rgba(59, 130, 246, 0.12), transparent 60%),
    radial-gradient(800px 500px at 90% 90%, rgba(139, 92, 246, 0.1), transparent 55%);
}
.auth-card {
  width: 100%;
  max-width: 400px;
  padding: 36px 32px;
}
.auth-brand {
  text-align: center;
  margin-bottom: 24px;
}
.auth-logo {
  font-size: 42px;
}
.auth-brand h1 {
  margin: 8px 0 4px;
  font-size: 22px;
}
.auth-brand p {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary);
}
.auth-footer {
  margin-top: 16px;
  text-align: center;
  font-size: 13px;
  color: var(--text-secondary);
}
.demo-accounts {
  display: flex;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
}
</style>
