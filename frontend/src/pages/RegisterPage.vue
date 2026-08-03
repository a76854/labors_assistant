<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NForm, NFormItem, NInput, NRadio, NRadioGroup, NSelect, useMessage } from 'naive-ui'
import { register } from '@/services/authService'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const message = useMessage()
const auth = useAuthStore()

const specialtyOptions = [
  { label: '劳动报酬纠纷', value: 'wage_arrears' },
  { label: '劳动合同争议', value: 'labor_contract' },
  { label: '工伤赔偿', value: 'work_injury' },
]
const regionOptions = [
  { label: '北京', value: 'beijing' },
  { label: '上海', value: 'shanghai' },
  { label: '广东', value: 'guangdong' },
]

const form = ref({
  username: '',
  password: '',
  confirm: '',
  role: 'user' as 'user' | 'lawyer',
  name: '',
  phone: '',
  specialty: [] as string[],
  region: null as string | null,
})
const loading = ref(false)

async function handleRegister() {
  if (form.value.username.length < 2) {
    message.warning('用户名至少 2 个字符')
    return
  }
  if (form.value.password.length < 6) {
    message.warning('密码至少 6 位')
    return
  }
  if (form.value.password !== form.value.confirm) {
    message.warning('两次输入的密码不一致')
    return
  }
  if (form.value.role === 'lawyer' && form.value.specialty.length === 0) {
    message.warning('请选择至少一个擅长领域')
    return
  }
  loading.value = true
  try {
    const data = await register({
      username: form.value.username,
      password: form.value.password,
      role: form.value.role,
      name: form.value.name || undefined,
      phone: form.value.phone || undefined,
      specialty: form.value.role === 'lawyer' ? form.value.specialty : undefined,
      region: form.value.role === 'lawyer' ? form.value.region || undefined : undefined,
    })
    auth.setAuth(data.access_token, data.user)
    message.success('注册成功')
    router.push(data.user.role === 'lawyer' ? '/lawyer/dashboard' : '/')
  } catch (error) {
    message.error(error instanceof Error ? error.message : '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card glass-card fade-in">
      <div class="auth-brand">
        <span class="auth-logo">⚖️</span>
        <h1>注册账号</h1>
        <p>劳动者与律师均可注册</p>
      </div>

      <n-form :model="form" label-placement="top" size="large" @keyup.enter="handleRegister">
        <n-form-item label="角色">
          <n-radio-group v-model:value="form.role">
            <n-radio value="user">我是劳动者</n-radio>
            <n-radio value="lawyer">我是律师</n-radio>
          </n-radio-group>
        </n-form-item>
        <n-form-item label="用户名">
          <n-input v-model:value="form.username" placeholder="2-50 个字符" />
        </n-form-item>
        <n-form-item label="密码">
          <n-input v-model:value="form.password" type="password" show-password-on="click" placeholder="至少 6 位" />
        </n-form-item>
        <n-form-item label="确认密码">
          <n-input v-model:value="form.confirm" type="password" show-password-on="click" placeholder="再次输入密码" />
        </n-form-item>
        <n-form-item label="姓名（选填）">
          <n-input v-model:value="form.name" placeholder="真实姓名或机构名称" />
        </n-form-item>
        <n-form-item label="联系电话（选填）">
          <n-input v-model:value="form.phone" placeholder="用于律师与您联系" />
        </n-form-item>

        <template v-if="form.role === 'lawyer'">
          <n-form-item label="擅长领域（决定系统推荐匹配）">
            <n-select
              v-model:value="form.specialty"
              :options="specialtyOptions"
              multiple
              placeholder="选择擅长领域，系统将优先推荐对应案件"
            />
          </n-form-item>
          <n-form-item label="所在地区（决定地区匹配）">
            <n-select
              v-model:value="form.region"
              :options="regionOptions"
              placeholder="选择所在地区，优先推荐本地案件"
            />
          </n-form-item>
        </template>

        <n-button type="primary" block size="large" :loading="loading" @click="handleRegister">
          注 册
        </n-button>
      </n-form>

      <div class="auth-footer">
        <span>已有账号？</span>
        <n-button text type="primary" @click="router.push('/login')">去登录</n-button>
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
  max-width: 440px;
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
</style>
