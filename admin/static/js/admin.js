/**
 * Admin interface JavaScript - Progressive enhancement
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Tile Generation Server Admin Interface loaded');
    
    // Add any interactive functionality here
    // For now, just basic logging for debugging
    
    // Example: Add click tracking for admin actions
    const actionButtons = document.querySelectorAll('.btn, .action-card, .access-card');
    actionButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            console.log('Admin action:', e.target.textContent?.trim() || 'Unknown action');
        });
    });
    
    // Example: Show loading states for long operations
    const regionCards = document.querySelectorAll('.region-card');
    regionCards.forEach(card => {
        card.addEventListener('click', function() {
            console.log('Region selected:', card.querySelector('h3')?.textContent);
        });
    });
});