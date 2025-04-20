// src/services/robotService.ts
import axios from 'axios';
import { Robot, RobotUpdate } from '../models/Robot';

const API_URL = import.meta.env.VITE_ROBOT_API_URL || 'http://robot.local';

export default {
  getAllRobots() {
    return axios.get<Robot[]>(`${API_URL}/robots`);
  },
  
  addRobot(robot: Robot) {
    return axios.post<Robot>(`${API_URL}/robots`, robot);
  },
  
  updateRobot(id: string, updates: RobotUpdate) {
    return axios.patch<Robot>(`${API_URL}/robot/${id}`, updates);
  }
};