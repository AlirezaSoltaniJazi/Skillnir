"""Supported AI tools registry page."""

from nicegui import ui

from skillnir.tools import TOOLS
from skillnir.ui.components.page_header import page_header
from skillnir.ui.layout import header


@ui.page('/tools')
def page_tools():
    _audio, _snd = header()

    with ui.column().classes('w-full max-w-6xl mx-auto px-8 py-8 gap-6'):
        page_header(
            'Tools Registry',
            f'{len(TOOLS)} AI tools supported (+ .agents/ auto-inject)',
            icon='devices',
        )

        # ── Search filter ──
        search_input = (
            ui.input(
                placeholder='Search tools...',
                on_change=lambda e: _filter_table(e.value),
            )
            .classes('w-64')
            .props('outlined dense rounded clearable')
        )

        columns = [
            {
                'name': 'name',
                'label': 'Name',
                'field': 'name',
                'sortable': True,
                'align': 'left',
            },
            {
                'name': 'company',
                'label': 'Company',
                'field': 'company',
                'sortable': True,
                'align': 'left',
            },
            {
                'name': 'dotdir',
                'label': 'Dotdir',
                'field': 'dotdir',
                'sortable': True,
                'align': 'left',
            },
            {
                'name': 'popularity',
                'label': 'Popularity',
                'field': 'popularity',
                'sortable': True,
            },
            {
                'name': 'performance',
                'label': 'Performance',
                'field': 'performance',
                'sortable': True,
            },
            {'name': 'price', 'label': 'Price', 'field': 'price', 'sortable': True},
        ]

        all_rows = [
            {
                'name': t.name,
                'company': t.company,
                'dotdir': t.dotdir + '/',
                'popularity': t.popularity,
                'performance': t.performance,
                'price': t.price,
                'icon_url': t.icon_url,
            }
            for t in TOOLS
        ]

        table = (
            ui.table(
                columns=columns,
                rows=all_rows,
                row_key='name',
                pagination={'rowsPerPage': 50},
            )
            .classes('w-full')
            .props('dense separator=cell')
        )

        table.add_slot(
            'body-cell-name',
            """
            <q-td :props="props">
                <div class="row items-center no-wrap q-gutter-sm">
                    <q-avatar size="24px" v-if="props.row.icon_url">
                        <img :src="props.row.icon_url">
                    </q-avatar>
                    <q-avatar size="24px" color="primary" text-color="white" v-else>
                        {{ props.row.name[0] }}
                    </q-avatar>
                    <span>{{ props.row.name }}</span>
                </div>
            </q-td>
        """,
        )

        # Score coloring slots
        for col in ('popularity', 'performance', 'price'):
            table.add_slot(
                f'body-cell-{col}',
                """
                <q-td :props="props">
                    <q-badge
                        :color="props.value >= 8 ? 'positive' : props.value >= 5 ? 'warning' : 'negative'"
                        :label="props.value"
                        dense
                    />
                </q-td>
            """,
            )

        def _filter_table(query: str) -> None:
            q = (query or '').lower()
            if not q:
                table.rows = all_rows
            else:
                table.rows = [
                    r
                    for r in all_rows
                    if q in r['name'].lower() or q in r['company'].lower()
                ]
            table.update()
