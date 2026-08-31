/* Smart Health Companion — shared "rising particles" background effect.
   Soft dots drift upward with a gentle sideways wobble and fade in/out,
   like bubbles on a vitals monitor. No connecting lines (kept distinct
   from the dashboard's particle-network effect). Usage:

   createRisingParticles(canvasEl, containerEl, { ...optional overrides });
*/
(function () {
    function createRisingParticles(canvas, container, opts) {
        if (!canvas || !container) return;
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

        const options = Object.assign({
            density: 22000,
            maxCount: 55,
            minCount: 16,
            teal: '27,122,114',
            coral: '255,90,78',
            coralRatio: 0.22,
            speedMin: 0.15,
            speedMax: 0.55,
            wobbleAmp: 14,
            radiusMin: 1,
            radiusMax: 2.6,
            maxAlpha: 0.55,
            edgeFade: 60
        }, opts || {});

        const ctx = canvas.getContext('2d');
        let width = 0, height = 0, dpr = 1;
        let particles = [];
        let rafId = null;
        let running = false;

        function spawn(initial) {
            const isCoral = Math.random() < options.coralRatio;
            return {
                baseX: Math.random() * width,
                y: initial ? Math.random() * height : height + Math.random() * 40,
                speed: options.speedMin + Math.random() * (options.speedMax - options.speedMin),
                r: options.radiusMin + Math.random() * (options.radiusMax - options.radiusMin) + (isCoral ? 0.4 : 0),
                wobbleAmp: options.wobbleAmp * (0.4 + Math.random() * 0.6),
                wobbleSpeed: 0.4 + Math.random() * 0.6,
                phase: Math.random() * Math.PI * 2,
                isCoral
            };
        }

        function makeParticles() {
            const count = Math.min(options.maxCount, Math.max(options.minCount, Math.round((width * height) / options.density)));
            particles = Array.from({ length: count }, () => spawn(true));
        }

        function resize() {
            const rect = container.getBoundingClientRect();
            width = Math.max(1, Math.round(rect.width));
            height = Math.max(1, Math.round(rect.height));
            dpr = Math.min(2, window.devicePixelRatio || 1);
            canvas.width = width * dpr;
            canvas.height = height * dpr;
            ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
            makeParticles();
        }

        function step(t) {
            if (!running) return;
            ctx.clearRect(0, 0, width, height);

            for (let i = 0; i < particles.length; i++) {
                let p = particles[i];
                p.y -= p.speed;

                if (p.y < -20) {
                    particles[i] = spawn(false);
                    continue;
                }

                const x = p.baseX + Math.sin((t / 1000) * p.wobbleSpeed + p.phase) * p.wobbleAmp;
                const fadeIn = Math.min(1, (height - p.y) / options.edgeFade);
                const fadeOut = Math.min(1, p.y / options.edgeFade);
                const alpha = Math.max(0, Math.min(fadeIn, fadeOut)) * options.maxAlpha;

                const color = p.isCoral ? options.coral : options.teal;
                ctx.fillStyle = `rgba(${color},${alpha})`;
                ctx.beginPath();
                ctx.arc(x, p.y, p.r, 0, Math.PI * 2);
                ctx.fill();
            }

            rafId = requestAnimationFrame(step);
        }

        function start() {
            if (running) return;
            running = true;
            rafId = requestAnimationFrame(step);
        }

        function stop() {
            running = false;
            if (rafId) cancelAnimationFrame(rafId);
            rafId = null;
        }

        resize();
        start();

        // Track the container's actual box size directly — this is what keeps
        // the canvas correctly sized through font-swap reflow, the container
        // being laid out at 0 size before first paint, responsive breakpoint
        // changes, etc. Far more reliable than only listening for window resize.
        let resizeTimer = null;
        const scheduleResize = () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(resize, 100);
        };

        if ('ResizeObserver' in window) {
            new ResizeObserver(scheduleResize).observe(container);
        } else {
            window.addEventListener('resize', scheduleResize);
        }

        if (document.fonts && document.fonts.ready) {
            document.fonts.ready.then(resize);
        }

        document.addEventListener('visibilitychange', () => {
            if (document.hidden) stop(); else start();
        });

        if ('IntersectionObserver' in window) {
            const io = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) start(); else stop();
                });
            }, { threshold: 0.01 });
            io.observe(container);
        }
    }

    window.createRisingParticles = createRisingParticles;
})();
