/**
 * OrderFlow - Interactive Tag Input Component
 * Turns colour and size inputs into interactive tags/chips.
 * Typing a name and pressing Enter or comma converts it to a tag and clears the input,
 * immediately giving space to enter more items.
 */

function setupTagInput(container) {
    if (!container || container.dataset.tagInitialized === 'true') {
        return;
    }

    const hiddenInput = container.querySelector('input[type="hidden"]');
    const textInput = container.querySelector('input[type="text"]');
    const tagsWrapper = container.querySelector('.tags-wrapper');

    if (!hiddenInput || !textInput || !tagsWrapper) {
        return;
    }

    container.dataset.tagInitialized = 'true';

    // Store tags array in memory
    let tags = [];

    // Initialize from hidden input value (if any)
    if (hiddenInput.value && hiddenInput.value.trim() !== '') {
        tags = hiddenInput.value
            .split(',')
            .map(t => t.trim())
            .filter(t => t.length > 0);
    }

    function syncHiddenInput() {
        hiddenInput.value = tags.join(', ');
        // Trigger change event for form tracking if needed
        hiddenInput.dispatchEvent(new Event('change', { bubbles: true }));
    }

    function renderTags() {
        // Clear all tag pills except input
        tagsWrapper.querySelectorAll('.tag-pill').forEach(el => el.remove());

        // Render each tag
        tags.forEach((tag, index) => {
            const pill = document.createElement('span');
            pill.className = 'tag-pill inline-flex items-center px-2 py-0.5 rounded bg-slate-900 text-white text-xs font-medium mr-1.5 mb-1 shadow-xs transition animate-in fade-in duration-150';
            
            const textSpan = document.createElement('span');
            textSpan.textContent = tag;
            pill.appendChild(textSpan);

            const removeBtn = document.createElement('button');
            removeBtn.type = 'button';
            removeBtn.className = 'ml-1.5 text-slate-300 hover:text-white focus:outline-none text-xs font-bold leading-none';
            removeBtn.innerHTML = '&times;';
            removeBtn.setAttribute('aria-label', 'Remove ' + tag);
            removeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                removeTag(index);
            });
            pill.appendChild(removeBtn);

            // Insert before text input
            tagsWrapper.insertBefore(pill, textInput);
        });

        syncHiddenInput();
    }

    function addTag(value) {
        if (!value) return;
        const cleaned = value.trim().replace(/^,+|,+$/g, '');
        if (cleaned.length === 0) return;

        // Support pasting or entering multiple comma-separated values
        const parts = cleaned.split(',').map(p => p.trim()).filter(p => p.length > 0);
        let added = false;

        parts.forEach(part => {
            // Check if already in tags (case-insensitive check)
            const exists = tags.some(t => t.toLowerCase() === part.toLowerCase());
            if (!exists) {
                tags.push(part);
                added = true;
            }
        });

        if (added) {
            renderTags();
        }
        textInput.value = '';
    }

    function removeTag(index) {
        if (index >= 0 && index < tags.length) {
            tags.splice(index, 1);
            renderTags();
            textInput.focus();
        }
    }

    // Keydown handler on text input
    textInput.addEventListener('keydown', (e) => {
        // Enter key or Comma key creates a tag
        if (e.key === 'Enter' || e.key === ',') {
            e.preventDefault();
            addTag(textInput.value);
        } else if (e.key === 'Backspace' && textInput.value === '' && tags.length > 0) {
            // Remove last tag when pressing backspace on empty input
            removeTag(tags.length - 1);
        }
    });

    // Handle blur (add pending text if user clicks outside)
    textInput.addEventListener('blur', () => {
        if (textInput.value.trim() !== '') {
            addTag(textInput.value);
        }
    });

    // Clicking anywhere on the container focuses the text input
    container.addEventListener('click', () => {
        textInput.focus();
    });

    // Expose addTag method on the container element for preset buttons
    container.addTag = addTag;

    // Initial render
    renderTags();
}

// Automatically initialize all tag input containers on page load
function initAllTagInputs(root = document) {
    root.querySelectorAll('.tag-input-container').forEach(container => {
        setupTagInput(container);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    initAllTagInputs();
});

