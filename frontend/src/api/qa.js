import request from './request'

export function generateRepairAdvice(data) {
  return request.post('/api/qa/repair-advice', data)
}
