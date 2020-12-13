'use strict';

/* Register a radio button (sourceName, sourceValue) that activates (shows/hides) an element (destinationId). */
function registerActivatorRadio(sourceName, sourceValue, destinationId, activatorMode) {
    const nodes = document.querySelectorAll("[name=" + sourceName + "][value=" + sourceValue + "]");
    registerActivator(nodes, destinationId, activatorMode);
}

/* Register a checkbox (sourceName) that activates (shows/hides) an element (destinationId). */
function registerActivatorCheckbox(sourceName, destinationId, activatorMode) {
    const nodes = document.querySelectorAll("[name=" + sourceName + "]");
    registerActivator(nodes, destinationId, activatorMode);
}

/* Register nodes as an activator for destinationId. Available modes:
 * show -- shows the element if the activator is checked
 * hide -- shows the element if the activator is unchecked
 * inverse -- hides the element if the activator is checked and shows if the activator is unchecked
 * undefined (default) -- shows the element if the activator is checked and hides if the activator is unchecked
 */
function registerActivator(nodes, destinationId, activatorMode) {
    const dest = document.getElementById(destinationId);
    if (nodes.length === 0 || dest === null) return;
    nodes.forEach(node => {
        node.addEventListener("change", ev => {
            if (activatorMode === "show") {
                if (ev.target.checked === true) {
                    dest.classList.remove("d-none");
                }
            } else if (activatorMode === "hide") {
                if (ev.target.checked === true) {
                    dest.classList.add("d-none");
                }
            } else if (activatorMode === "inverse") {
                if (ev.target.checked === true) {
                    dest.classList.add("d-none");
                } else {
                    dest.classList.remove("d-none");
                }
            } else {
                if (ev.target.checked === true) {
                    dest.classList.remove("d-none");
                } else {
                    dest.classList.add("d-none");
                }
            }
        });
    });
}

/* Activate a Bootstrap tab, based on the URL fragment. */
function showTabFromFragment() {
    const fragment = new URL(document.location).hash;
    if (fragment.length > 2) {
        $(fragment + "-tab").tab("show");
    }
}
