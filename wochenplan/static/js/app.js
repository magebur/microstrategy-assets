/* wochenplan.net - Frontend JavaScript */

// --- Stepper Controls ---
document.querySelectorAll('.stepper-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const target = document.getElementById(btn.dataset.target);
        if (!target) return;
        const min = parseInt(target.min);
        const max = parseInt(target.max);
        let val = parseInt(target.value);

        if (btn.dataset.action === 'increase' && val < max) {
            target.value = val + 1;
        } else if (btn.dataset.action === 'decrease' && val > min) {
            target.value = val - 1;
        }
    });
});

// --- Recipe Swap ---
function swapRecipe(planId, dayIndex, currentRecipeId, button) {
    const card = button.closest('.plan-card');
    card.classList.add('is-loading');
    button.disabled = true;

    fetch('/swap', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            plan_id: planId,
            day_index: dayIndex,
            current_recipe_id: currentRecipeId
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            const r = data.recipe;
            card.dataset.recipeId = r.id;

            // Update card content
            const title = card.querySelector('.card-title a');
            title.textContent = r.name;
            title.href = '/recipe/' + r.id;

            card.querySelector('.card-description').textContent = r.description;

            const meta = card.querySelector('.card-meta');
            let metaHtml = `<span class="meta-time">${r.prep_time_minutes + r.cook_time_minutes} Min</span>`;
            metaHtml += `<span class="meta-difficulty">${r.difficulty}</span>`;
            if (r.is_vegetarian) metaHtml += '<span class="meta-tag tag-veg">vegetarisch</span>';
            if (r.cost_level === 'guenstig') metaHtml += '<span class="meta-tag tag-cheap">g\u00fcnstig</span>';
            else if (r.cost_level === 'teuer') metaHtml += '<span class="meta-tag tag-expensive">teuer</span>';
            meta.innerHTML = metaHtml;

            const ingredients = card.querySelector('.card-ingredients');
            if (ingredients && r.ingredients) {
                ingredients.innerHTML = '<span class="ingredients-label">Zutaten:</span> ' +
                    r.ingredients.map(i => i.name).join(', ');
            }

            // Update swap button onclick
            button.setAttribute('onclick',
                `swapRecipe(${planId}, ${dayIndex}, ${r.id}, this)`);
        }
        card.classList.remove('is-loading');
        button.disabled = false;
    })
    .catch(() => {
        card.classList.remove('is-loading');
        button.disabled = false;
    });
}

// --- Shopping List: Toggle Item ---
function toggleItem(itemId, checked) {
    const item = document.querySelector(`[data-item-id="${itemId}"]`);

    fetch('/toggle_item', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_id: itemId, checked: checked })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            if (checked) {
                item.classList.add('is-checked');
            } else {
                item.classList.remove('is-checked');
            }
            updateRemainingCount();
        }
    });
}

// --- Check All Staple Items ---
function checkAllStaples() {
    document.querySelectorAll('.check-item.is-staple').forEach(item => {
        const checkbox = item.querySelector('.check-checkbox');
        if (!checkbox.checked) {
            checkbox.checked = true;
            const itemId = parseInt(checkbox.dataset.itemId);
            toggleItem(itemId, true);
        }
    });
}

// --- Update Remaining Count ---
function updateRemainingCount() {
    const total = document.querySelectorAll('.check-item').length;
    const checked = document.querySelectorAll('.check-item.is-checked').length;
    const remaining = total - checked;

    const countEl = document.getElementById('remaining-count');
    if (countEl) {
        countEl.textContent = remaining;
    }

    const doneEl = document.getElementById('check-done');
    if (doneEl) {
        doneEl.style.display = remaining === 0 ? 'block' : 'none';
    }
}
