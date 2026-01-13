import React from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, Button, Typography } from 'antd'
import { ArrowLeftOutlined } from '@ant-design/icons'

const { Title } = Typography

const TestSuiteDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/test-suites')}
          style={{ marginRight: 16 }}
        >
          返回
        </Button>
        <Title level={4} style={{ display: 'inline-block', margin: 0 }}>
          套件详情
        </Title>
      </div>
      <Card>
        <p>套件ID: {id}</p>
        <p>更多详情功能开发中...</p>
      </Card>
    </div>
  )
}

export default TestSuiteDetail
