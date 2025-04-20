export interface Robot {
    id: string;
    name: string;
    status: string;
  }
  
  export interface RobotUpdate {
    name?: string;
    status?: string;
  }