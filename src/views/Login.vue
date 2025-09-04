<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
// import { loginApi } from '@/api/public'

const router = useRouter()
// 登录表单数据
const loginForm = reactive({
  username: '',
  password: ''
})


// 登录处理
const login = async () => {
  if (!loginForm.username || !loginForm.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  try {
    const result = await loginApi({
      username: loginForm.username,
      password: loginForm.password,
    })

    if (result.code === 1) {
      // 保存用户信息到本地存储
      localStorage.setItem('loginUser', JSON.stringify(result.data))

      // 记录用户登录日志（直接调用后端接口）
      try {
        // 这里可以调用后端接口记录登录日志
        // await recordUserLoginApi(result.data.id)
        console.log('用户登录成功')
      } catch (error) {
        console.error('记录用户登录日志失败:', error)
      }

      // 跳转至对应角色页面
      router.push(`/home`)
    }
    else {
      ElMessage.error('用户或密码不正确')
    }
  } catch (error) {
    console.error('登录失败:', error)
    ElMessage.error('登录失败，请稍后重试')
  }
}

// 返回入口界面
const back = () => {
  loginForm.username = ''
  loginForm.password = ''
  router.back()
}

// 忘记密码
const reset = () => {
  router.push(`/reset?mode=forget&role=${role.value}`)
}
</script>

<template>
  <div id="container">
    <div class="login-form page-transition">
      <el-form label-width="80px">
        <p class="title">用户登录</p>
        <el-form-item label="用户名">
          <el-input v-model="loginForm.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="密码">
          <el-input type="password" v-model="loginForm.password" placeholder="请输入密码"></el-input>
        </el-form-item>
        <div class="button-group">
          <el-button class="login-button back-btn" type="primary" @click="back">返回</el-button>
          <!-- <el-button class="login-button forgot-btn" type="primary" @click="reset">忘记密码</el-button> -->
          <el-button class="login-button login-btn" type="primary" @click="login">登录</el-button>
        </div>
        <div class="register-link">
          <span>还没有账号？请联系相关负责人</span>
        </div>
      </el-form>
    </div>
  </div>
</template>


<!-- <style scoped>
/* 引入FontAwesome */
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');

#container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 100vh;
  padding: 90px 20px 20px 20px;
  width: 100%;
}

.enter_select_card {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 60px;
}

.welcome-text {
  text-align: center;
  margin-bottom: 40px;
}

.welcome-title {
  font-size: 32px;
  font-weight: 500;
  color: #333;
  margin: 0 0 12px 0;
  letter-spacing: 0.05em;
}

.welcome-subtitle {
  font-size: 24px;
  font-weight: 400;
  color: rgba(0, 0, 0, 0.85);
  margin: 0;
  letter-spacing: 0.02em;
}

.cards-container {
  display: flex;
  gap: 32px;
  justify-content: center;
  align-items: center;
}

.card {
  width: 240px;
  background: #fff;
  border-radius: 22px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
  padding: 32px 18px 28px 18px;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: transform 0.22s, box-shadow 0.22s;
  position: relative;
  overflow: hidden;
}

.card:hover {
  transform: translateY(-8px) scale(1.05);
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.25);
}

.card-student {
  background: #f0f0f0;
}

.card-design {
  background: #f0f0f0;
}

.card-admin {
  background: #f0f0f0;
}

.icon {
  width: 56px;
  height: 56px;
  margin-bottom: 18px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(0, 0, 0, 0.1);
}

.icon i {
  font-size: 28px;
  color: #333;
}

.card-title {
  font-size: 22px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

.card-subtitle {
  font-size: 15px;
  color: rgba(0, 0, 0, 0.7);
  margin-bottom: 18px;
}

.card-btn {
  width: 100%;
  border-radius: 16px;
  font-size: 1.1em;
  transition: all 0.18s;
  border: none;
  color: #333;
  font-weight: 600;
}

.card-btn-student {
  background: rgba(0, 0, 0, 0.1);
}

.card-btn-student:hover {
  background: rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
}

.card-btn-teacher {
  background: rgba(0, 0, 0, 0.1);
}

.card-btn-teacher:hover {
  background: rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
}

.card-btn-admin {
  background: rgba(0, 0, 0, 0.1);
}

.card-btn-admin:hover {
  background: rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
}

.login-form {
  width: 370px;
  background: #fff;
  padding: 36px 32px 28px 32px;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.13);
  position: relative;
  margin-top: 90px;
}

.page-transition {
  animation: page-fade-in 0.7s cubic-bezier(.4, 0, .2, 1);
}

@keyframes page-fade-in {
  0% {
    opacity: 0;
    transform: translateY(40px) scale(0.98);
  }

  100% {
    opacity: 1;
    transform: none;
  }
}

@keyframes card-fade-in {
  0% {
    opacity: 0;
    transform: translateY(40px) scale(0.98);
  }

  100% {
    opacity: 1;
    transform: none;
  }
}

.title {
  font-size: 26px;
  font-weight: 700;
  text-align: center;
  margin-bottom: 24px;
  color: #333;
  letter-spacing: 0.04em;
}

.el-form-item {
  margin-bottom: 18px;
}

.button-group {
  display: flex;
  gap: 12px;
  justify-content: space-between;
  margin-top: 24px;
}

.login-button {
  flex: 1;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  border: none;
}

.back-btn {
  background: rgb(254, 254, 254);
  color: #666;
}

.back-btn:hover {
  background: rgb(228, 228, 228);
  transform: translateY(-1px);
}

.forgot-btn {
  background: #f0f0f0;
  color: #333;
}

.forgot-btn:hover {
  background: #e0e0e0;
  transform: translateY(-1px);
}

.login-btn {
  background: #f0f0f0;
  color: #333;
}

.login-btn:hover {
  background: #e0e0e0;
  transform: translateY(-1px);
}

.register-link {
  text-align: center;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.register-link span {
  color: #666;
  font-size: 14px;
}

.register-btn {
  color: #333;
  text-decoration: none;
  font-weight: 500;
  margin-left: 8px;
  transition: all 0.2s;
}

.register-btn:hover {
  color: #666;
  text-decoration: underline;
}
</style> -->
