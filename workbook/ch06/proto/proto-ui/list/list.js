// from DOM
const taskInput = document.getElementById('taskInput');
const addTaskBtn = document.getElementById('addTaskBtn');
const taskList = document.getElementById('taskList');

// load tasks from localStorage
function loadTasks() {
  const tasks = JSON.parse(localStorage.getItem('tasks')) || [];
  tasks.forEach(task => {
    const li = document.createElement('li');
    li.textContent = task.text;

    // if task completed, mark with the 'completed' class
    if (task.completed) {
      li.classList.add('completed');
    }

    // add button to mark task as complete
    const completeBtn = document.createElement('button');
    completeBtn.textContent = 'Complete';
    completeBtn.onclick = function () {
      li.classList.toggle('completed');
      updateLocalStorage();
    };

    // add button to remove task
    const removeBtn = document.createElement('button');
    removeBtn.textContent = 'Remove';
    removeBtn.onclick = function () {
      taskList.removeChild(li);
      updateLocalStorage();
    };

    li.appendChild(completeBtn);
    li.appendChild(removeBtn);

    // append new task to task list
    taskList.appendChild(li);
  });
}

// update localStorage
function updateLocalStorage() {
  const tasks = [];
  const taskItems = taskList.getElementsByTagName('li');
  for (let i = 0; i < taskItems.length; i++) {
    const taskText = taskItems[i].firstChild.textContent; // task text
    const taskCompleted = taskItems[i].classList.contains('completed'); // completed?
    tasks.push({ text: taskText, completed: taskCompleted });
  }
  localStorage.setItem('tasks', JSON.stringify(tasks));
}

// add a new task
function addTask() {
  const taskText = taskInput.value.trim();
  if (taskText) {
    const li = document.createElement('li');
    li.textContent = taskText;

    // add a button to mark task complete
    const completeBtn = document.createElement('button');
    completeBtn.textContent = 'Complete';
    completeBtn.onclick = function () {
      li.classList.toggle('completed');
      updateLocalStorage();
    };

    // add a button to remove task
    const removeBtn = document.createElement('button');
    removeBtn.textContent = 'Remove';
    removeBtn.onclick = function () {
      taskList.removeChild(li);
      updateLocalStorage();
    };

    li.appendChild(completeBtn);
    li.appendChild(removeBtn);

    // append new task to task list
    taskList.appendChild(li);

    // clear input field after adding a task
    taskInput.value = '';

    // update localStorage after adding new task
    updateLocalStorage();
  }
}

addTaskBtn.addEventListener('click', addTask);

taskInput.addEventListener('keypress', function (e) {
  if (e.key === 'Enter') {
    addTask();
  }
});

// load tasks from localStorage when the page is loaded
document.addEventListener('DOMContentLoaded', loadTasks);
