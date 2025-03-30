/**
 * Home Workout Manager Library
 * A JavaScript library providing common functionality for the Home Workout Manager application
 */

// Use IIFE to avoid polluting the global namespace
const WorkoutManager = (function() {
    'use strict';

    // Private variables and functions
    let timerIntervals = {};

    /**
     * Toggles dark mode
     * @param {boolean} enableDark - Whether to enable dark mode
     */
    function toggleDarkMode(enableDark) {
        if (enableDark) {
            document.body.classList.add('dark-mode');
            localStorage.setItem('darkMode', 'true');
        } else {
            document.body.classList.remove('dark-mode');
            localStorage.setItem('darkMode', 'false');
        }
    }

    /**
     * Initializes dark mode based on saved preference
     */
    function initDarkMode() {
        const isDarkMode = localStorage.getItem('darkMode') === 'true';
        
        if (isDarkMode) {
            document.body.classList.add('dark-mode');
        }
        
        const darkModeToggle = document.getElementById('darkModeToggle');
        if (darkModeToggle) {
            darkModeToggle.checked = isDarkMode;
            
            darkModeToggle.addEventListener('change', function() {
                toggleDarkMode(this.checked);
            });
        }
    }

    /**
     * Formats time in seconds to MM:SS format
     * @param {number} seconds - Time in seconds
     * @returns {string} Formatted time string
     */
    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
    }

    /**
     * Creates and starts a timer
     * @param {string} elementId - ID of the element to display the timer
     * @param {function} callback - Optional callback when timer updates
     * @returns {string} Timer ID
     */
    function startTimer(elementId, callback) {
        const timerElement = document.getElementById(elementId);
        if (!timerElement) return null;
        
        let seconds = 0;
        const timerId = `timer-${Date.now()}`;
        
        timerIntervals[timerId] = setInterval(() => {
            seconds++;
            const timeString = formatTime(seconds);
            timerElement.textContent = timeString;
            
            if (callback && typeof callback === 'function') {
                callback(seconds, timeString);
            }
        }, 1000);
        
        return timerId;
    }

    /**
     * Pauses a timer
     * @param {string} timerId - ID of the timer to pause
     */
    function pauseTimer(timerId) {
        if (timerIntervals[timerId]) {
            clearInterval(timerIntervals[timerId]);
        }
    }

    /**
     * Resumes a timer
     * @param {string} timerId - ID of the timer to resume
     * @param {string} elementId - ID of the element to display the timer
     * @param {function} callback - Optional callback when timer updates
     */
    function resumeTimer(timerId, elementId, callback) {
        if (timerIntervals[timerId]) {
            pauseTimer(timerId);
            return startTimer(elementId, callback);
        }
        return null;
    }

    /**
     * Creates a countdown timer
     * @param {string} elementId - ID of the element to display the countdown
     * @param {number} duration - Duration in seconds
     * @param {function} onComplete - Callback when countdown completes
     * @param {function} onTick - Optional callback on each tick
     * @returns {string} Timer ID
     */
    function startCountdown(elementId, duration, onComplete, onTick) {
        const element = document.getElementById(elementId);
        if (!element) return null;
        
        let seconds = duration;
        element.textContent = seconds;
        
        const timerId = `countdown-${Date.now()}`;
        
        timerIntervals[timerId] = setInterval(() => {
            seconds--;
            element.textContent = seconds;
            
            if (onTick && typeof onTick === 'function') {
                onTick(seconds);
            }
            
            if (seconds <= 0) {
                clearInterval(timerIntervals[timerId]);
                delete timerIntervals[timerId];
                
                if (onComplete && typeof onComplete === 'function') {
                    onComplete();
                }
            }
        }, 1000);
        
        return timerId;
    }

    /**
     * Shows a notification
     * @param {string} title - Notification title
     * @param {string} body - Notification body
     * @param {boolean} useNative - Whether to use native notifications (if available)
     */
    function showNotification(title, body, useNative = true) {
        if (useNative && 'Notification' in window && Notification.permission === 'granted') {
            new Notification(title, { body });
        } else {
            // Fallback to custom notification
            const notification = document.createElement('div');
            notification.className = 'workout-notification fade-in';
            notification.innerHTML = `
                <div class="notification-content">
                    <h4>${title}</h4>
                    <p>${body}</p>
                </div>
                <button class="notification-close">&times;</button>
            `;
            
            document.body.appendChild(notification);
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                notification.classList.add('fade-out');
                setTimeout(() => {
                    document.body.removeChild(notification);
                }, 300);
            }, 5000);
            
            // Close button
            const closeBtn = notification.querySelector('.notification-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => {
                    notification.classList.add('fade-out');
                    setTimeout(() => {
                        document.body.removeChild(notification);
                    }, 300);
                });
            }
        }
    }

    /**
     * Requests notification permission
     * @returns {Promise} Promise that resolves with the permission status
     */
    function requestNotificationPermission() {
        if (!('Notification' in window)) {
            return Promise.resolve('denied');
        }
        
        if (Notification.permission === 'granted') {
            return Promise.resolve('granted');
        }
        
        return Notification.requestPermission();
    }

    /**
     * Makes an element draggable
     * @param {HTMLElement} element - The element to make draggable
     * @param {function} onDragEnd - Callback when dragging ends
     */
    function makeDraggable(element, onDragEnd) {
        if (!element) return;
        
        element.setAttribute('draggable', 'true');
        
        let draggedElement = null;
        
        element.addEventListener('dragstart', function(e) {
            draggedElement = this;
            setTimeout(() => {
                this.classList.add('dragging');
            }, 0);
            
            // Store data if needed
            if (e.dataTransfer) {
                e.dataTransfer.setData('text/plain', this.dataset.id || '');
            }
        });
        
        element.addEventListener('dragend', function() {
            this.classList.remove('dragging');
            
            if (onDragEnd && typeof onDragEnd === 'function') {
                onDragEnd(this);
            }
            
            draggedElement = null;
        });
    }

    /**
     * Makes a container accept draggable items
     * @param {HTMLElement} container - The container element
     * @param {function} onDrop - Callback when an item is dropped
     */
    function makeDroppable(container, onDrop) {
        if (!container) return;
        
        container.addEventListener('dragover', function(e) {
            e.preventDefault();
            const draggable = document.querySelector('.dragging');
            
            if (draggable) {
                const afterElement = getDragAfterElement(container, e.clientY);
                
                if (afterElement == null) {
                    container.appendChild(draggable);
                } else {
                    container.insertBefore(draggable, afterElement);
                }
            }
        });
        
        container.addEventListener('drop', function(e) {
            e.preventDefault();
            
            if (onDrop && typeof onDrop === 'function') {
                const draggable = document.querySelector('.dragging');
                if (draggable) {
                    onDrop(draggable, e);
                }
            }
        });
        
        function getDragAfterElement(container, y) {
            const draggableElements = [...container.querySelectorAll('[draggable]:not(.dragging)')];
            
            return draggableElements.reduce((closest, child) => {
                const box = child.getBoundingClientRect();
                const offset = y - box.top - box.height / 2;
                
                if (offset < 0 && offset > closest.offset) {
                    return { offset: offset, element: child };
                } else {
                    return closest;
                }
            }, { offset: Number.NEGATIVE_INFINITY }).element;
        }
    }

    /**
     * Plays a sound effect
     * @param {string} sound - Name of the sound ('beep', 'complete', 'error')
     */
    function playSound(sound) {
        const sounds = {
            beep: '/static/sounds/beep.mp3',
            complete: '/static/sounds/complete.mp3',
            error: '/static/sounds/error.mp3'
        };
        
        if (sounds[sound]) {
            const audio = new Audio(sounds[sound]);
            audio.play().catch(e => console.log('Error playing sound:', e));
        }
    }

    /**
     * Initializes charts using Chart.js
     * @param {string} elementId - ID of the canvas element
     * @param {Object} data - Chart data
     * @param {Object} options - Chart options
     * @returns {Object} Chart instance
     */
    function initChart(elementId, data, options = {}) {
        const element = document.getElementById(elementId);
        if (!element || !element.getContext) return null;
        
        // Check if Chart.js is available
        if (typeof Chart === 'undefined') {
            console.error('Chart.js is not loaded');
            return null;
        }
        
        return new Chart(element.getContext('2d'), {
            ...data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                ...options
            }
        });
    }

    /**
     * Shows a confirmation dialog
     * @param {string} message - Confirmation message
     * @param {function} onConfirm - Callback when confirmed
     * @param {function} onCancel - Callback when canceled
     */
    function confirmAction(message, onConfirm, onCancel) {
        // Create a Bootstrap modal if available
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            // Check if a modal already exists
            let modal = document.querySelector('#workoutConfirmModal');
            
            if (!modal) {
                // Create the modal
                modal = document.createElement('div');
                modal.className = 'modal fade';
                modal.id = 'workoutConfirmModal';
                modal.setAttribute('tabindex', '-1');
                modal.setAttribute('aria-hidden', 'true');
                
                modal.innerHTML = `
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">Confirm Action</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <p id="workoutConfirmMessage"></p>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" id="workoutConfirmCancel">Cancel</button>
                                <button type="button" class="btn btn-primary" id="workoutConfirmOk">Confirm</button>
                            </div>
                        </div>
                    </div>
                `;
                
                document.body.appendChild(modal);
            }
            
            // Set the message
            const messageElement = modal.querySelector('#workoutConfirmMessage');
            if (messageElement) {
                messageElement.textContent = message;
            }
            
            // Initialize the modal
            const modalInstance = new bootstrap.Modal(modal);
            
            // Add event listeners
            const confirmButton = modal.querySelector('#workoutConfirmOk');
            const cancelButton = modal.querySelector('#workoutConfirmCancel');
            
            const confirmHandler = function() {
                if (onConfirm && typeof onConfirm === 'function') {
                    onConfirm();
                }
                modalInstance.hide();
                confirmButton.removeEventListener('click', confirmHandler);
                cancelButton.removeEventListener('click', cancelHandler);
            };
            
            const cancelHandler = function() {
                if (onCancel && typeof onCancel === 'function') {
                    onCancel();
                }
                confirmButton.removeEventListener('click', confirmHandler);
                cancelButton.removeEventListener('click', cancelHandler);
            };
            
            confirmButton.addEventListener('click', confirmHandler);
            cancelButton.addEventListener('click', cancelHandler);
            
            // Show the modal
            modalInstance.show();
            
            // Add event listener for modal hidden event
            modal.addEventListener('hidden.bs.modal', function() {
                cancelHandler();
            }, { once: true });
        } else {
            // Fallback to native confirm
            if (confirm(message)) {
                if (onConfirm && typeof onConfirm === 'function') {
                    onConfirm();
                }
            } else {
                if (onCancel && typeof onCancel === 'function') {
                    onCancel();
                }
            }
        }
    }

    /**
     * Initializes the workout manager
     */
    function init() {
        initDarkMode();
        
        // Request notification permission
        if ('Notification' in window && Notification.permission !== 'granted' && Notification.permission !== 'denied') {
            // Wait for user interaction before requesting permission
            document.addEventListener('click', function firstInteraction() {
                requestNotificationPermission();
                document.removeEventListener('click', firstInteraction);
            }, { once: true });
        }
        
        // Add notification styles
        const style = document.createElement('style');
        style.textContent = `
            .workout-notification {
                position: fixed;
                top: 20px;
                right: 20px;
                max-width: 350px;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                z-index: 9999;
                overflow: hidden;
                transition: opacity 0.3s, transform 0.3s;
                opacity: 1;
                transform: translateY(0);
            }
            
            .workout-notification.fade-out {
                opacity: 0;
                transform: translateY(-20px);
            }
            
            .workout-notification .notification-content {
                padding: 16px;
            }
            
            .workout-notification h4 {
                margin: 0 0 8px 0;
                font-size: 16px;
                font-weight: 600;
            }
            
            .workout-notification p {
                margin: 0;
                font-size: 14px;
                color: #555;
            }
            
            .workout-notification .notification-close {
                position: absolute;
                top: 10px;
                right: 10px;
                background: none;
                border: none;
                font-size: 18px;
                cursor: pointer;
                color: #aaa;
            }
            
            .dark-mode .workout-notification {
                background-color: #333;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            }
            
            .dark-mode .workout-notification h4 {
                color: #eee;
            }
            
            .dark-mode .workout-notification p {
                color: #bbb;
            }
        `;
        
        document.head.appendChild(style);
    }

    // Public API
    return {
        init,
        toggleDarkMode,
        formatTime,
        startTimer,
        pauseTimer,
        resumeTimer,
        startCountdown,
        showNotification,
        requestNotificationPermission,
        makeDraggable,
        makeDroppable,
        playSound,
        initChart,
        confirmAction
    };
})();

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', WorkoutManager.init);