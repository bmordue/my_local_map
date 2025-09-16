// Interactive Map JavaScript
class LumsdenTouristMap {
    constructor() {
        this.map = null;
        this.layers = {};
        this.baseMapLayer = null;
        this.markers = {};
        
        this.initializeMap();
        this.setupControls();
        this.loadMapData();
    }
    
    initializeMap() {
        // Initialize the map with OpenStreetMap tiles as default
        this.map = L.map('map').setView(
            window.mapConfig.center, 
            13
        );
        
        // Add OpenStreetMap base layer
        const osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 18,
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);
        
        // Add custom base map overlay if available
        this.loadBaseMapOverlay();
        
        // Fit to bounding box
        const bbox = window.mapConfig.bbox;
        this.map.fitBounds([
            [bbox.south, bbox.west],
            [bbox.north, bbox.east]
        ]);
    }
    
    loadBaseMapOverlay() {
        // Check if base map image is available
        fetch('/map_image')
            .then(response => {
                if (response.ok) {
                    const bbox = window.mapConfig.bbox;
                    this.baseMapLayer = L.imageOverlay('/map_image', [
                        [bbox.south, bbox.west],
                        [bbox.north, bbox.east]
                    ], {
                        opacity: 0.8,
                        interactive: false
                    });
                    
                    // Add to map initially if checkbox is checked
                    if (document.getElementById('show-base-map').checked) {
                        this.baseMapLayer.addTo(this.map);
                    }
                }
            })
            .catch(error => {
                console.log('Base map image not available:', error);
            });
    }
    
    setupControls() {
        // Layer control checkboxes
        const controls = {
            'show-attractions': 'attractions',
            'show-accommodation': 'accommodation', 
            'show-dining': 'dining',
            'show-activities': 'activities',
            'show-trails': 'trails',
            'show-base-map': 'baseMap'
        };
        
        Object.entries(controls).forEach(([checkboxId, layerName]) => {
            const checkbox = document.getElementById(checkboxId);
            checkbox.addEventListener('change', (e) => {
                this.toggleLayer(layerName, e.target.checked);
            });
        });
    }
    
    async loadMapData() {
        const layers = ['attractions', 'accommodation', 'dining', 'activities', 'trails'];
        
        for (const layer of layers) {
            try {
                const response = await fetch(`/api/data/${layer}`);
                const data = await response.json();
                this.createLayer(layer, data);
            } catch (error) {
                console.warn(`Failed to load ${layer} data:`, error);
            }
        }
    }
    
    createLayer(layerName, geojsonData) {
        const markerStyles = {
            attractions: { color: '#e74c3c', icon: '🏛️' },
            accommodation: { color: '#3498db', icon: '🏨' },
            dining: { color: '#f39c12', icon: '🍽️' },
            activities: { color: '#9b59b6', icon: '🎯' },
            trails: { color: '#27ae60', icon: '🥾' }
        };
        
        const style = markerStyles[layerName] || { color: '#333', icon: '📍' };
        
        this.layers[layerName] = L.geoJSON(geojsonData, {
            pointToLayer: (feature, latlng) => {
                return this.createCustomMarker(latlng, style, feature.properties);
            },
            onEachFeature: (feature, layer) => {
                if (feature.properties) {
                    const popup = this.createPopupContent(feature.properties);
                    layer.bindPopup(popup);
                    
                    // Add click handler for info panel
                    layer.on('click', () => {
                        this.showInfoPanel(feature.properties);
                    });
                }
            }
        });
        
        // Add to map if checkbox is checked
        const checkboxId = `show-${layerName}`;
        if (document.getElementById(checkboxId).checked) {
            this.layers[layerName].addTo(this.map);
        }
    }
    
    createCustomMarker(latlng, style, properties) {
        const markerHtml = `
            <div class="${properties.category || 'default'}-marker" 
                 style="width: 25px; height: 25px; 
                        background: ${style.color}; 
                        border: 2px solid white;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 12px;
                        box-shadow: 0 2px 6px rgba(0,0,0,0.3);">
                ${style.icon}
            </div>
        `;
        
        return L.divIcon({
            html: markerHtml,
            className: 'custom-marker',
            iconSize: [25, 25],
            iconAnchor: [12.5, 12.5]
        });
    }
    
    createPopupContent(properties) {
        const rating = properties.rating ? '⭐'.repeat(Math.floor(properties.rating)) : '';
        
        return `
            <div class="poi-popup">
                <h3>${properties.name || 'Unnamed Location'}</h3>
                ${properties.category ? `<div class="category">${properties.category}</div>` : ''}
                ${rating ? `<div class="rating">${rating} (${properties.rating}/5)</div>` : ''}
                ${properties.description ? `<div class="description">${properties.description}</div>` : ''}
                <div class="details">
                    ${properties.opening_hours ? `<div><strong>Hours:</strong> ${properties.opening_hours}</div>` : ''}
                    ${properties.price ? `<div><strong>Price:</strong> ${properties.price}</div>` : ''}
                    ${properties.phone ? `<div><strong>Phone:</strong> ${properties.phone}</div>` : ''}
                    ${properties.website ? `<div><a href="${properties.website}" class="website" target="_blank">Visit Website</a></div>` : ''}
                </div>
            </div>
        `;
    }
    
    showInfoPanel(properties) {
        const panel = document.getElementById('info-panel');
        const content = document.getElementById('info-content');
        
        const rating = properties.rating ? '⭐'.repeat(Math.floor(properties.rating)) : '';
        
        content.innerHTML = `
            <h3>${properties.name || 'Unnamed Location'}</h3>
            ${properties.category ? `<div class="category">${properties.category}</div>` : ''}
            ${rating ? `<div class="rating">${rating} (${properties.rating}/5)</div>` : ''}
            ${properties.description ? `<div class="description">${properties.description}</div>` : ''}
            <div class="details">
                ${properties.opening_hours ? `<div><strong>Opening Hours:</strong> ${properties.opening_hours}</div>` : ''}
                ${properties.price ? `<div><strong>Price Range:</strong> ${properties.price}</div>` : ''}
                ${properties.phone ? `<div><strong>Phone:</strong> ${properties.phone}</div>` : ''}
                ${properties.email ? `<div><strong>Email:</strong> ${properties.email}</div>` : ''}
                ${properties.website ? `<div><a href="${properties.website}" class="website" target="_blank">Visit Website</a></div>` : ''}
                ${properties.amenities ? `<div><strong>Amenities:</strong> ${properties.amenities}</div>` : ''}
                ${properties.cuisine ? `<div><strong>Cuisine:</strong> ${properties.cuisine}</div>` : ''}
                ${properties.difficulty ? `<div><strong>Difficulty:</strong> ${properties.difficulty}</div>` : ''}
                ${properties.distance ? `<div><strong>Distance:</strong> ${properties.distance}</div>` : ''}
            </div>
        `;
        
        panel.classList.remove('hidden');
    }
    
    toggleLayer(layerName, show) {
        if (layerName === 'baseMap') {
            if (this.baseMapLayer) {
                if (show) {
                    this.baseMapLayer.addTo(this.map);
                } else {
                    this.map.removeLayer(this.baseMapLayer);
                }
            }
            return;
        }
        
        if (this.layers[layerName]) {
            if (show) {
                this.layers[layerName].addTo(this.map);
            } else {
                this.map.removeLayer(this.layers[layerName]);
            }
        }
    }
}

// Initialize the map when the page loads
document.addEventListener('DOMContentLoaded', function() {
    new LumsdenTouristMap();
    
    // Setup info panel close button
    document.getElementById('close-panel').addEventListener('click', function() {
        document.getElementById('info-panel').classList.add('hidden');
    });
    
    console.log('Lumsden Interactive Tourist Map loaded successfully');
});