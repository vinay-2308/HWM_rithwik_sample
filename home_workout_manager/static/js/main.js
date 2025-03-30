/**
 * Setup main workout timer
 */
function setupWorkoutTimer() {
    const startTimerBtn = document.getElementById('startTimerBtn');
    const pauseTimerBtn = document.getElementById('pauseTimerBtn');
    const resetTimerBtn = document.getElementById('resetTimerBtn');
    const workoutTimerDisplay = document.getElementById('workoutTimer');
    const totalWorkoutTimeDisplay = document.getElementById('totalWorkoutTime');
    const workoutDurationInput = document.getElementById('workoutDurationInput');
    
    if (!startTimerBtn || !pauseTimerBtn || !resetTimerBtn || !workoutTimerDisplay) {
        return; // Exit if elements don't exist
    }
    
    let seconds = 0;
    let timerInterval;
    let isRunning = false;
    
    startTimerBtn.addEventListener('click', function() {
        if (!isRunning) {
            isRunning = true;
            timerInterval = setInterval(updateTimer, 1000);
            startTimerBtn.disabled = true;
            pauseTimerBtn.disabled = false;
            resetTimerBtn.disabled = false;
            
            // Add active class for visual feedback
            startTimerBtn.classList.add('active');
            pauseTimerBtn.classList.remove('active');
        }
    });
    
    pauseTimerBtn.addEventListener('click', function() {
        if (isRunning) {
            clearInterval(timerInterval);
            isRunning = false;
            startTimerBtn.disabled = false;
            pauseTimerBtn.disabled = true;
            
            // Add active class for visual feedback
            pauseTimerBtn.classList.add('active');
            startTimerBtn.classList.remove('active');
        }
    });
    
    resetTimerBtn.addEventListener('click', function() {
        clearInterval(timerInterval);
        isRunning = false;
        seconds = 0;
        updateTimerDisplay();
        startTimerBtn.disabled = false;
        pauseTimerBtn.disabled = true;
        resetTimerBtn.disabled = true;
        
        // Remove active classes
        startTimerBtn.classList.remove('active');
        pauseTimerBtn.classList.remove('active');
    });
    
    function updateTimer() {
        seconds++;
        updateTimerDisplay();
    }
    
    function updateTimerDisplay() {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        const formattedTime = `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
        
        workoutTimerDisplay.textContent = formattedTime;
        
        // Update other timer-related elements if they exist
        if (totalWorkoutTimeDisplay) {
            totalWorkoutTimeDisplay.textContent = formattedTime;
        }
        
        if (workoutDurationInput) {
            workoutDurationInput.value = seconds;
        }
    }
}

/**
 * Setup rest timer functionality
 */
function setupRestTimer() {
    const restTimerContainer = document.getElementById('restTimerContainer');
    const restTimerDisplay = document.getElementById('restTimer');
    
    if (!restTimerContainer || !restTimerDisplay) {
        return; // Exit if elements don't exist
    }
    
    window.startRestTimer = function(duration) {
        // Clear any existing interval
        if (window.restTimerInterval) {
            clearInterval(window.restTimerInterval);
        }
        
        let seconds = duration;
        restTimerDisplay.textContent = seconds;
        restTimerContainer.style.display = 'block';
        
        // Add visual pulse effect
        restTimerContainer.classList.add('pulse-animation');
        
        // Add progress bar if it doesn't exist
        let progressBar = restTimerContainer.querySelector('.progress');
        if (!progressBar) {
            progressBar = document.createElement('div');
            progressBar.className = 'progress mt-2';
            progressBar.innerHTML = '<div class="progress-bar"></div>';
            restTimerContainer.appendChild(progressBar);
        }
        
        const progressBarInner = progressBar.querySelector('.progress-bar');
        progressBarInner.style.width = '100%';
        progressBarInner.style.transition = `width ${duration}s linear`;
        
        // Update progress bar
        setTimeout(() => {
            progressBarInner.style.width = '0%';
        }, 50); // Small delay to ensure the transition works
        
        // Start countdown
        window.restTimerInterval = setInterval(function() {
            seconds--;
            restTimerDisplay.textContent = seconds;
            
            // Update color based on remaining time
            if (seconds <= 5) {
                restTimerDisplay.classList.add('text-danger');
            } else {
                restTimerDisplay.classList.remove('text-danger');
            }
            
            if (seconds <= 0) {
                clearInterval(window.restTimerInterval);
                completeRestTimer();
            }
        }, 1000);
    };
    
    function completeRestTimer() {
        // Play sound
        playSound('/static/sounds/beep.mp3');
        
        // Add completion animation
        restTimerContainer.classList.add('complete-animation');
        
        // Show notification
        showNotification('Rest Complete', 'Time to start your next set!');
        
        // Reset after animation completes
        setTimeout(() => {
            restTimerContainer.style.display = 'none';
            restTimerContainer.classList.remove('pulse-animation', 'complete-animation');
            restTimerDisplay.classList.remove('text-danger');
        }, 3000);
    }
}

/**
 * Play a sound file
 * @param {string} soundPath - Path to the sound file
 */
function playSound(soundPath) {
    const audio = new Audio(soundPath);
    audio.play().catch(e => {
        console.log('Error playing sound:', e);
    });
}

/**
 * Show a browser notification
 * @param {string} title - Notification title
 * @param {string} body - Notification body text
 */
function showNotification(title, body) {
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, {
            body: body,
            icon: '/static/images/logo.png'
        });
    }
}

/**
 * Set up drag and drop functionality for exercise reordering
 */
function setupDragAndDrop() {
    const exerciseList = document.getElementById('exerciseList');
    
    if (!exerciseList) {
        return; // Exit if element doesn't exist
    }
    
    let draggedItem = null;
    
    // Add event listeners to all exercise items
    const exerciseItems = exerciseList.querySelectorAll('.exercise-item');
    exerciseItems.forEach(item => {
        // Make items draggable
        item.setAttribute('draggable', 'true');
        
        // Add drag event listeners
        item.addEventListener('dragstart', handleDragStart);
        item.addEventListener('dragend', handleDragEnd);
        item.addEventListener('dragover', handleDragOver);
        item.addEventListener('dragenter', handleDragEnter);
        item.addEventListener('dragleave', handleDragLeave);
        item.addEventListener('drop', handleDrop);
    });
    
    function handleDragStart(e) {
        draggedItem = this;
        this.classList.add('dragging');
        
        // Add subtle transition effects
        exerciseItems.forEach(item => {
            if (item !== draggedItem) {
                item.classList.add('drag-active');
            }
        });
        
        // Set data transfer properties
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/html', this.innerHTML);
    }
    
    function handleDragEnd() {
        this.classList.remove('dragging');
        
        // Remove transition effects
        exerciseItems.forEach(item => {
            item.classList.remove('drag-active');
        });
        
        draggedItem = null;
        
        // Update order in the database
        updateExerciseOrder();
    }
    
    function handleDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        return false;
    }
    
    function handleDragEnter(e) {
        e.preventDefault();
        this.classList.add('drag-over');
    }
    
    function handleDragLeave() {
        this.classList.remove('drag-over');
    }
    
    function handleDrop(e) {
        e.stopPropagation();
        
        if (draggedItem !== this) {
            // Get positions
            const allItems = [...exerciseList.querySelectorAll('.exercise-item')];
            const draggedIndex = allItems.indexOf(draggedItem);
            const targetIndex = allItems.indexOf(this);
            
            // Reorder based on position
            if (draggedIndex < targetIndex) {
                this.parentNode.insertBefore(draggedItem, this.nextSibling);
            } else {
                this.parentNode.insertBefore(draggedItem, this);
            }
            
            // Add animation effect
            draggedItem.classList.add('drop-animation');
            setTimeout(() => {
                draggedItem.classList.remove('drop-animation');
            }, 300);
        }
        
        this.classList.remove('drag-over');
        return false;
    }
    
    function updateExerciseOrder() {
        const items = exerciseList.querySelectorAll('.exercise-item');
        const exerciseIds = Array.from(items).map(item => item.dataset.id);
        
        // CSRF token for the AJAX request
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // Send AJAX request to update order
        fetch('/update-exercise-order/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: 'exercise_ids=' + JSON.stringify(exerciseIds)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Show success feedback
                showToast('Exercise order updated', 'success');
            } else {
                console.error('Error updating exercise order:', data.message);
                showToast('Failed to update exercise order', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Failed to update exercise order', 'danger');
        });
    }
}

/**
 * Set up charts for the progress page
 */
function setupCharts() {
    const workoutDistributionChart = document.getElementById('workoutDistributionChart');
    const weightProgressChart = document.getElementById('weightProgressChart');
    
    if (workoutDistributionChart) {
        setupWorkoutDistributionChart(workoutDistributionChart);
    }
    
    if (weightProgressChart) {
        setupWeightProgressChart(weightProgressChart);
    }
}

/**
 * Set up workout distribution chart
 * @param {HTMLElement} canvas - The canvas element
 */
function setupWorkoutDistributionChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    // Check if the chart data is available in a data attribute
    let chartData;
    try {
        chartData = JSON.parse(canvas.dataset.chartData || '[]');
    } catch (e) {
        // If parsing fails, use sample data
        chartData = [3, 4, 2, 5, 1, 2, 0];
    }
    
    // Check for theme preference
    const isDarkMode = document.body.classList.contains('dark-mode');
    const textColor = isDarkMode ? '#e0e0e0' : '#495057';
    const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
    
    // Create chart
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            datasets: [{
                label: 'Workouts by Day of Week',
                data: chartData,
                backgroundColor: [
                    'rgba(67, 97, 238, 0.7)',
                    'rgba(72, 149, 239, 0.7)',
                    'rgba(76, 201, 240, 0.7)',
                    'rgba(67, 97, 238, 0.7)',
                    'rgba(72, 149, 239, 0.7)',
                    'rgba(76, 201, 240, 0.7)',
                    'rgba(67, 97, 238, 0.7)'
                ],
                borderColor: [
                    'rgb(67, 97, 238)',
                    'rgb(72, 149, 239)',
                    'rgb(76, 201, 240)',
                    'rgb(67, 97, 238)',
                    'rgb(72, 149, 239)',
                    'rgb(76, 201, 240)',
                    'rgb(67, 97, 238)'
                ],
                borderWidth: 1,
                borderRadius: 6,
                hoverBackgroundColor: 'rgba(247, 37, 133, 0.7)',
                hoverBorderColor: 'rgb(247, 37, 133)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: isDarkMode ? 'rgba(33, 37, 41, 0.9)' : 'rgba(255, 255, 255, 0.9)',
                    titleColor: isDarkMode ? '#e0e0e0' : '#212529',
                    bodyColor: isDarkMode ? '#e0e0e0' : '#212529',
                    borderColor: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            const value = context.raw;
                            return value + (value === 1 ? ' workout' : ' workouts');
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0,
                        color: textColor,
                        font: {
                            family: "'Inter', sans-serif",
                            size: 12
                        }
                    },
                    grid: {
                        color: gridColor
                    }
                },
                x: {
                    ticks: {
                        color: textColor,
                        font: {
                            family: "'Inter', sans-serif",
                            size: 12
                        }
                    },
                    grid: {
                        color: gridColor
                    }
                }
            },
            animation: {
                duration: 1500,
                easing: 'easeOutQuart'
            }
        }
    });
    
    // Update chart when theme changes
    document.addEventListener('themeChange', function(e) {
        const isDarkMode = e.detail.darkMode;
        const textColor = isDarkMode ? '#e0e0e0' : '#495057';
        const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
        
        chart.options.scales.y.ticks.color = textColor;
        chart.options.scales.x.ticks.color = textColor;
        chart.options.scales.y.grid.color = gridColor;
        chart.options.scales.x.grid.color = gridColor;
        
        chart.options.plugins.tooltip.backgroundColor = isDarkMode ? 'rgba(33, 37, 41, 0.9)' : 'rgba(255, 255, 255, 0.9)';
        chart.options.plugins.tooltip.titleColor = isDarkMode ? '#e0e0e0' : '#212529';
        chart.options.plugins.tooltip.bodyColor = isDarkMode ? '#e0e0e0' : '#212529';
        
        chart.update();
    });
}

/**
 * Show a toast message
 * @param {string} message - Message to display
 * @param {string} type - Type of toast (success, danger, warning, info)
 */
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.id = toastId;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    // Create toast content
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    // Add to container
    toastContainer.appendChild(toast);
    
    // Initialize and show toast
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: 5000
    });
    bsToast.show();
    
    // Remove from DOM after hiding
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

/**
 * Filter workout history table
 * @param {string} filter - Filter type ('all', 'week', 'month')
 */
window.filterWorkouts = function(filter) {
    const table = document.getElementById('workoutHistoryTable');
    if (!table) return;
    
    const rows = table.querySelectorAll('tbody tr');
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const startOfWeek = new Date(today);
    startOfWeek.setDate(today.getDate() - today.getDay()); // Start of week (Sunday)
    const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
    
    rows.forEach(row => {
        const dateCell = row.cells[0].textContent;
        const date = new Date(dateCell);
        
        if (filter === 'all') {
            showRowWithAnimation(row);
        } else if (filter === 'week' && date >= startOfWeek) {
            showRowWithAnimation(row);
        } else if (filter === 'month' && date >= startOfMonth) {
            showRowWithAnimation(row);
        } else {
            hideRow(row);
        }
    });
    
    // Update active button
    document.querySelectorAll('.btn-group .btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`.btn-group .btn[onclick="filterWorkouts('${filter}')"]`).classList.add('active');
};

/**
 * Show a table row with animation
 * @param {HTMLElement} row - The row to show
 */
function showRowWithAnimation(row) {
    // First set opacity to 0 but display to table-row
    row.style.display = 'table-row';
    row.style.opacity = '0';
    
    // Force a reflow to make the animation work
    void row.offsetWidth;
    
    // Now animate the opacity
    row.style.transition = 'opacity 0.3s ease';
    row.style.opacity = '1';
}

/**
 * Hide a table row
 * @param {HTMLElement} row - The row to hide
 */
function hideRow(row) {
    row.style.opacity = '0';
    
    // Wait for the animation to complete before actually hiding
    setTimeout(() => {
        row.style.display = 'none';
    }, 300);
}