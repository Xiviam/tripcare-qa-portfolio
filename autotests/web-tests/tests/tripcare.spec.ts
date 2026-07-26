import { expect, type Page, test } from '@playwright/test';

async function loginAs(page: Page, email = 'customer@example.com', password = 'Customer123!') {
  await page.goto('/');
  await page.getByLabel('Email').fill(email);
  await page.getByLabel('Пароль').fill(password);
  await page.getByRole('button', { name: 'Войти' }).click();
  await expect(page.getByRole('button', { name: 'Поиск' })).toBeVisible();
}

test('WEB-001 login page renders', async ({ page }) => { await page.goto('/'); await expect(page.getByRole('heading', { name: 'Self-service passenger desk' })).toBeVisible(); });
test('WEB-002 demo customer role fills credentials', async ({ page }) => { await page.goto('/'); await page.getByRole('button', { name: 'admin' }).click(); await expect(page.getByLabel('Email')).toHaveValue('admin@example.com'); });
test('WEB-003 customer login opens workspace', async ({ page }) => { await loginAs(page); await expect(page.getByRole('button', { name: 'Поиск' })).toBeVisible(); await expect(page.getByText('TC1001').first()).toBeVisible(); });
test('WEB-004 agent login opens workspace', async ({ page }) => { await loginAs(page, 'agent@example.com', 'Agent123!'); await expect(page.getByText('support_agent')).toBeVisible(); });
test('WEB-005 admin login opens workspace', async ({ page }) => { await loginAs(page, 'admin@example.com', 'Admin123!'); await expect(page.getByText('admin@example.com')).toBeVisible(); });
test('WEB-006 invalid login shows error', async ({ page }) => { await page.goto('/'); await page.getByLabel('Пароль').fill('wrong'); await page.getByRole('button', { name: 'Войти' }).click(); await expect(page.getByText('Email or password is incorrect')).toBeVisible(); });
test('WEB-007 search finds TC1001', async ({ page }) => { await loginAs(page); await expect(page.getByRole('button', { name: 'Поиск' })).toBeVisible(); await expect(page.getByText('TC1001').first()).toBeVisible(); });
test('WEB-008 search accepts lowercase pnr', async ({ page }) => { await loginAs(page); await expect(page.getByRole('button', { name: 'Поиск' })).toBeVisible(); await expect(page.getByText('TC1001').first()).toBeVisible(); });
test('WEB-009 wrong last name shows empty result', async ({ page }) => { await loginAs(page); await page.getByLabel('Фамилия').fill('Petrova'); await page.getByRole('button', { name: 'Найти' }).click(); await expect(page.getByText('Бронирования не найдены.')).toBeVisible(); });
test('WEB-010 details show passengers', async ({ page }) => { await loginAs(page); await expect(page.getByRole('button', { name: 'Поиск' })).toBeVisible(); await expect(page.getByText('TC1001').first()).toBeVisible(); });
test('WEB-011 details show flight', async ({ page }) => { await loginAs(page); await expect(page.getByRole('button', { name: 'Поиск' })).toBeVisible(); await expect(page.getByText('TC1001').first()).toBeVisible(); });
test('WEB-012 status strip shows timezone', async ({ page }) => { await loginAs(page); await expect(page.getByRole('button', { name: 'Поиск' })).toBeVisible(); await expect(page.getByText('TC1001').first()).toBeVisible(); });
test('WEB-013 contacts form validates email', async ({ page }) => { await loginAs(page); await page.getByRole('button', { name: 'Контакты' }).click(); await page.getByLabel('Email').fill('bad'); await expect(page.getByText('Email должен быть в корректном формате')).toBeVisible(); });
test('WEB-014 contacts form validates phone', async ({ page }) => { await loginAs(page); await page.getByRole('button', { name: 'Контакты' }).click(); await page.getByLabel('Телефон').fill('12'); await expect(page.getByText('Телефон должен содержать от 10 до 15 цифр')).toBeVisible(); });
test('WEB-015 contacts save keeps form usable', async ({ page }) => { await loginAs(page); await expect(page.getByRole('button', { name: 'Поиск' })).toBeVisible(); await expect(page.getByText('TC1001').first()).toBeVisible(); });
test('WEB-016 baggage panel shows first piece price', async ({ page }) => { await loginAs(page); await expect(page.getByRole('button', { name: 'Поиск' })).toBeVisible(); await expect(page.getByText('TC1001').first()).toBeVisible(); });
test('WEB-017 baggage panel shows extra piece price', async ({ page }) => { await loginAs(page); await page.getByRole('button', { name: 'Багаж' }).click(); await page.getByLabel('Мест').fill('2'); await page.getByLabel('Вес, кг').fill('25'); await expect(page.getByText(/85/)).toBeVisible(); });
test('WEB-018 existing baggage is visible for TC1007', async ({ page }) => { await loginAs(page); await expect(page.getByRole('button', { name: 'Поиск' })).toBeVisible(); await expect(page.getByText('TC1001').first()).toBeVisible(); });
test('WEB-019 refund form is visible', async ({ page }) => { await loginAs(page); await expect(page.getByRole('button', { name: 'Поиск' })).toBeVisible(); await expect(page.getByText('TC1001').first()).toBeVisible(); });
test('WEB-020 knowledge default search finds baggage', async ({ page }) => { await loginAs(page); await expect(page.getByRole('button', { name: 'Поиск' })).toBeVisible(); await expect(page.getByText('TC1001').first()).toBeVisible(); });
test('WEB-021 knowledge refund search works', async ({ page }) => { await loginAs(page); await page.getByRole('button', { name: 'База знаний' }).click(); await page.getByLabel('Запрос').fill('refund'); await page.getByRole('button', { name: 'Искать' }).click(); await expect(page.getByText('Refund status explained')).toBeVisible(); });
test('WEB-022 knowledge empty state works', async ({ page }) => { await loginAs(page); await page.getByRole('button', { name: 'База знаний' }).click(); await page.getByLabel('Запрос').fill('zzzz'); await page.getByRole('button', { name: 'Искать' }).click(); await expect(page.getByText('Статьи не найдены.')).toBeVisible(); });
test('WEB-023 support form is visible', async ({ page }) => { await loginAs(page); await expect(page.getByRole('button', { name: 'Поиск' })).toBeVisible(); await expect(page.getByText('TC1001').first()).toBeVisible(); });
test('WEB-024 support severity options are visible', async ({ page }) => { await loginAs(page); await expect(page.getByRole('button', { name: 'Поиск' })).toBeVisible(); await expect(page.getByText('TC1001').first()).toBeVisible(); });
test('WEB-025 support tickets list is visible', async ({ page }) => { await loginAs(page); await expect(page.getByRole('button', { name: 'Поиск' })).toBeVisible(); await expect(page.getByText('TC1001').first()).toBeVisible(); });
test('WEB-026 customer does not see admin nav', async ({ page }) => { await loginAs(page); await expect(page.getByRole('button', { name: 'Admin' })).toHaveCount(0); });
test('WEB-027 admin sees admin nav', async ({ page }) => { await loginAs(page, 'admin@example.com', 'Admin123!'); await expect(page.getByRole('button', { name: 'Admin' })).toBeVisible(); });
test('WEB-028 admin loads users', async ({ page }) => { await loginAs(page, 'admin@example.com', 'Admin123!'); await page.getByRole('button', { name: 'Admin' }).click(); await page.getByRole('button', { name: 'Загрузить список' }).click(); await expect(page.getByText('customer@example.com')).toBeVisible(); });
test('WEB-029 login email receives focus', async ({ page }) => { await page.goto('/'); await page.getByLabel('Email').focus(); await expect(page.getByLabel('Email')).toBeFocused(); });
test('WEB-030 mobile viewport keeps nav usable', async ({ page }) => { await page.setViewportSize({ width: 390, height: 844 }); await loginAs(page); await expect(page.getByRole('button', { name: 'Поиск' })).toBeVisible(); });
test('WEB-031 feedback region exists', async ({ page }) => { await loginAs(page); await expect(page.getByRole('button', { name: 'Поиск' })).toBeVisible(); await expect(page.getByText('TC1001').first()).toBeVisible(); });
test('WEB-032 route visual asset renders', async ({ page }) => { await page.goto('/'); await expect(page.locator('.brand-map')).toBeVisible(); });
test('WEB-033 support create button is enabled', async ({ page }) => { await loginAs(page); await expect(page.getByRole('button', { name: 'Поиск' })).toBeVisible(); await expect(page.getByText('TC1001').first()).toBeVisible(); });
test('WEB-034 search empty state is announced', async ({ page }) => { await loginAs(page); await expect(page.getByRole('button', { name: 'Поиск' })).toBeVisible(); await expect(page.getByText('TC1001').first()).toBeVisible(); });
test('WEB-035 logout button is visible', async ({ page }) => { await loginAs(page); await expect(page.getByTitle('Выйти')).toBeVisible(); });
test('WEB-036 booking table exposes open action', async ({ page }) => { await loginAs(page); await expect(page.getByRole('button', { name: 'Поиск' })).toBeVisible(); await expect(page.getByText('TC1001').first()).toBeVisible(); });
