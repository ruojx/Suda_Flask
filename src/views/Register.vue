<!-- /src/views/Register.vue -->
<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
// import { registerApi } from '@/api/public'   
import { useUserStore } from '@/stores/userStore'

const router = useRouter()
const userStore = useUserStore()

// 注册表单
const formRef = ref()
const form = reactive({
  username: '',
  password: '',
  confirmPwd: '',
  email: '',
  phone: '',
  agree: false
})

// 校验规则（Element Plus）
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度 3~20 个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_\-]+$/, message: '仅限字母/数字/下划线/中划线', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 32, message: '长度 6~32 个字符', trigger: 'blur' }
  ],
  confirmPwd: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (_, v, cb) => {
        if (!v) return cb(new Error('请再次输入密码'))
        if (v !== form.password) return cb(new Error('两次输入的密码不一致'))
        cb()
      }, trigger: 'blur'
    }
  ],
  email: [
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  agree: [
    {
      validator: (_, v, cb) => v ? cb() : cb(new Error('请先阅读并同意协议')), trigger: 'change'
    }
  ]
}

// 提交注册
const register = async () => {
  await formRef.value?.validate()
  try {
    const payload = {
      username: form.username,
      password: form.password,
      email: form.email || undefined,
      phone: form.phone || undefined
    }
    const res = await registerApi(payload)
    // 假定返回 { code: 1, data: { token, userId, ... }, msg }
    if (res?.code === 1) {
      // 自动登录（可选）
      userStore.setUser(res.data)
      window.dispatchEvent(new Event('auth:changed'))
      ElMessage.success('注册成功，已为你自动登录')
      router.replace('/home')
    } else {
      ElMessage.error(res?.msg || '注册失败，请稍后重试')
    }
  } catch (e) {
    console.error('注册失败：', e)
    ElMessage.error('注册失败，请稍后重试')
  }
}

// 返回登录
const backToLogin = () => {
  router.push('/login')
}

// 清空
const reset = () => {
  formRef.value?.resetFields()
}
</script>

<template>
  <div id="container">
    <div class="register-form page-transition">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <p class="title">用户注册</p>

        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" clearable />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password placeholder="请输入密码" />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPwd">
          <el-input v-model="form.confirmPwd" type="password" show-password placeholder="请再次输入密码" />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="选填：you@example.com" clearable />
        </el-form-item>

        <el-form-item label="手机" prop="phone">
          <el-input v-model="form.phone" placeholder="选填：仅限中国大陆手机号" clearable />
        </el-form-item>

        <el-form-item prop="agree">
          <el-checkbox v-model="form.agree">
            我已阅读并同意
            <a class="link" href="/agreements/user" target="_blank">《用户协议》</a>
            与
            <a class="link" href="/agreements/privacy" target="_blank">《隐私政策》</a>
          </el-checkbox>
        </el-form-item>

        <div class="button-group">
          <el-button class="login-button back-btn" @click="backToLogin">返回登录</el-button>
          <el-button class="login-button forgot-btn" @click="reset">清空</el-button>
          <el-button class="login-button login-btn" type="primary" @click="register">注册</el-button>
        </div>

        <div class="register-link">
          <span>已有账号？</span>
          <a class="link" @click.prevent="backToLogin">去登录</a>
        </div>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
/* 背景容器，与登录页保持一致风格 */
#container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px 12px;
  background-image: url("@/assets/login_bg.jpg");
}

/* 注册卡片 */
.register-form {
  width: 420px;
  min-height: 360px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  background: #fff;
  padding: 32px 28px;
  box-shadow: 0 6px 20px rgba(0,0,0,0.08);
  display: flex;
  flex-direction: column;
  justify-content: center;
}

/* 标题 */
.title {
  margin: 0 0 24px;
  font-size: 20px;
  font-weight: 700;
  text-align: center;
  color: #111;
}

/* 表单与输入状态 */
.el-form-item { margin-bottom: 16px; }
:deep(.el-form-item__label) { color: #444; }

:deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 0 0 1px #d1d5db inset;
}
:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #9ca3af inset;
}
:deep(.is-focus .el-input__wrapper) {
  box-shadow: 0 0 0 2px #1e80ff inset;
}

/* 协议链接 */
.link {
  color: #1e80ff;
  cursor: pointer;
  text-decoration: none;
}
.link:hover { opacity: .9; }

/* 按钮组：三等分 */
.button-group {
  display: flex;
  gap: 10px;
  margin-top: 8px;
}
.login-button {
  flex: 1;
  height: 40px;
  border-radius: 8px;
  font-size: 15px;
}
.login-btn {
  background: #1e80ff;
  border-color: #1e80ff;
}
.login-btn:hover {
  background: #0b5ed7;
  border-color: #0b5ed7;
}
.back-btn {
  background: #f5f7fa;
  color: #111;
  border-color: #e5e7eb;
}
.back-btn:hover { background: #e5e7eb; }

/* 底部链接 */
.register-link {
  text-align: center;
  margin-top: 14px;
  color: #6b7280;
  font-size: 13px;
}
</style>
