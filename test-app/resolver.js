const db = require('./db');
const Query = {
  test: () => 'Test Success',
  sayHello: (root, args) => `Hello ${args.name}, GraphQL server says Hello to you`,
  greeting:() => { return 'Hello This is GrapgQL API, for is curricular unit !!'},

  students:() => db.students.list(),

  studentById:(root,args,context,info) => {
    return db.students.get(args.id);
  }
}

const Student = {
  fullName:(root,args,context,info) => {
    return root.firstName+" "+root.lastName
  },
  college:(root) => {
    return db.colleges.get(root.collegeId);
  }
}

const Mutation = { 
  createStudent:(root,args,context,info) => {
    return db.students.create({collegeId:args.collegeId,firstName:args.firstName,lastName:args.lastName});
  }
}
module.exports = {Query, Student, Mutation}