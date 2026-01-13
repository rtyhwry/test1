import React from 'react'
import { Card, Tabs, Form, Input, Button, Switch, message, Typography } from 'antd'

const { Title } = Typography
const { TabPane } = Tabs

const Settings: React.FC = () => {
  const [gitlabForm] = Form.useForm()
  const [almForm] = Form.useForm()
  const [artifactForm] = Form.useForm()

  const handleSave = (type: string) => {
    message.success(`${type}配置保存成功`)
  }

  return (
    <div>
      <Title level={4} style={{ marginBottom: 16 }}>系统设置</Title>

      <Card>
        <Tabs defaultActiveKey="gitlab">
          <TabPane tab="GitLab配置" key="gitlab">
            <Form
              form={gitlabForm}
              layout="vertical"
              style={{ maxWidth: 600 }}
              initialValues={{
                url: 'https://gitlab.example.com',
                default_branch: 'main',
              }}
            >
              <Form.Item name="url" label="GitLab地址">
                <Input placeholder="https://gitlab.example.com" />
              </Form.Item>
              <Form.Item name="token" label="Access Token">
                <Input.Password placeholder="请输入GitLab Access Token" />
              </Form.Item>
              <Form.Item name="default_branch" label="默认分支">
                <Input placeholder="main" />
              </Form.Item>
              <Form.Item>
                <Button type="primary" onClick={() => handleSave('GitLab')}>
                  保存配置
                </Button>
              </Form.Item>
            </Form>
          </TabPane>

          <TabPane tab="ALM配置" key="alm">
            <Form
              form={almForm}
              layout="vertical"
              style={{ maxWidth: 600 }}
            >
              <Form.Item name="url" label="ALM地址">
                <Input placeholder="https://alm.example.com" />
              </Form.Item>
              <Form.Item name="username" label="用户名">
                <Input placeholder="请输入用户名" />
              </Form.Item>
              <Form.Item name="password" label="密码">
                <Input.Password placeholder="请输入密码" />
              </Form.Item>
              <Form.Item name="project_id" label="项目ID">
                <Input placeholder="请输入ALM项目ID" />
              </Form.Item>
              <Form.Item name="auto_sync" label="自动同步" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item>
                <Button type="primary" onClick={() => handleSave('ALM')}>
                  保存配置
                </Button>
              </Form.Item>
            </Form>
          </TabPane>

          <TabPane tab="制品库配置" key="artifact">
            <Form
              form={artifactForm}
              layout="vertical"
              style={{ maxWidth: 600 }}
            >
              <Form.Item name="type" label="制品库类型">
                <Input placeholder="nexus / artifactory" />
              </Form.Item>
              <Form.Item name="url" label="制品库地址">
                <Input placeholder="https://nexus.example.com" />
              </Form.Item>
              <Form.Item name="repository" label="仓库名称">
                <Input placeholder="releases" />
              </Form.Item>
              <Form.Item name="username" label="用户名">
                <Input placeholder="请输入用户名" />
              </Form.Item>
              <Form.Item name="password" label="密码">
                <Input.Password placeholder="请输入密码" />
              </Form.Item>
              <Form.Item>
                <Button type="primary" onClick={() => handleSave('制品库')}>
                  保存配置
                </Button>
              </Form.Item>
            </Form>
          </TabPane>

          <TabPane tab="通知配置" key="notification">
            <Form layout="vertical" style={{ maxWidth: 600 }}>
              <Form.Item name="smtp_host" label="SMTP服务器">
                <Input placeholder="smtp.example.com" />
              </Form.Item>
              <Form.Item name="smtp_port" label="SMTP端口">
                <Input placeholder="587" />
              </Form.Item>
              <Form.Item name="smtp_user" label="用户名">
                <Input placeholder="请输入用户名" />
              </Form.Item>
              <Form.Item name="smtp_password" label="密码">
                <Input.Password placeholder="请输入密码" />
              </Form.Item>
              <Form.Item name="from_email" label="发件人邮箱">
                <Input placeholder="noreply@example.com" />
              </Form.Item>
              <Form.Item>
                <Button type="primary" onClick={() => handleSave('通知')}>
                  保存配置
                </Button>
              </Form.Item>
            </Form>
          </TabPane>
        </Tabs>
      </Card>
    </div>
  )
}

export default Settings
